import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import matplotlib.pyplot as plt

try:
    import plotly.express as px
except Exception:
    px = None


@dataclass(frozen=True)
class ConceptItem:
    label: str
    name: str
    description: str

    @property
    def text(self) -> str:
        base = f"{self.name}. {self.description}".strip()
        return base if base else self.name


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten_concept(concept: Dict[str, Any], prefix: str = "") -> List[ConceptItem]:
    name = str(concept.get("name", "")).strip() or "Unnamed"
    desc = str(concept.get("description", "")).strip()

    label = f"{prefix}{name}" if prefix else name
    items = [ConceptItem(label=label, name=name, description=desc)]

    subconcepts = concept.get("subconcepts", []) or []
    if not isinstance(subconcepts, list):
        return items

    for sub in subconcepts:
        if isinstance(sub, dict):
            items.extend(flatten_concept(sub, prefix=f"{label}/"))
    return items


def collect_items(data: Any, label_prefix: str = "") -> List[ConceptItem]:
    if isinstance(data, list):
        items: List[ConceptItem] = []
        for entry in data:
            if isinstance(entry, dict):
                items.extend(flatten_concept(entry, prefix=label_prefix))
        return items

    if isinstance(data, dict):
        if isinstance(data.get("concepts"), list):
            items = []
            for entry in data["concepts"]:
                if isinstance(entry, dict):
                    items.extend(flatten_concept(entry, prefix=label_prefix))
            return items
        return flatten_concept(data, prefix=label_prefix)

    return []


def compute_similarity_matrix(
    items_a: Sequence[ConceptItem],
    items_b: Sequence[ConceptItem],
) -> np.ndarray:
    if not items_a or not items_b:
        raise ValueError("No concepts found in one of the inputs.")

    texts_a = [item.text for item in items_a]
    texts_b = [item.text for item in items_b]

    corpus = texts_a + texts_b
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words=None,
        ngram_range=(1, 2),
        max_features=50000,
    )
    tfidf = vectorizer.fit_transform(corpus)

    vec_a = tfidf[: len(texts_a)]
    vec_b = tfidf[len(texts_a) :]

    return cosine_similarity(vec_a, vec_b)


def save_png_heatmap(
    similarity: np.ndarray,
    y_labels: Sequence[str],
    x_labels: Sequence[str],
    output_path: Path,
    dpi: int = 350,
    max_annotate_cells: int = 900,
) -> None:
    width = min(18, max(8, 0.35 * len(x_labels)))
    height = min(18, max(6, 0.35 * len(y_labels)))

    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    image = ax.imshow(similarity, aspect="auto", vmin=0.0, vmax=1.0, cmap="viridis")

    ax.set_title("Heatmap de Similaridade (Analogias)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Conceito B", fontsize=11)
    ax.set_ylabel("Conceito A", fontsize=11)

    ax.set_xticks(range(len(x_labels)))
    ax.set_yticks(range(len(y_labels)))
    ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(y_labels, fontsize=8)

    if similarity.size <= max_annotate_cells:
        for row in range(similarity.shape[0]):
            for col in range(similarity.shape[1]):
                ax.text(col, row, f"{similarity[row, col]:.2f}", ha="center", va="center", fontsize=7)

    cbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Similaridade (0-1)")

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def save_plotly_heatmap(
    similarity: np.ndarray,
    y_labels: Sequence[str],
    x_labels: Sequence[str],
    output_path: Path,
) -> None:
    if px is None:
        raise RuntimeError("plotly nao esta instalado. Rode: pip install plotly")

    fig = px.imshow(
        similarity,
        x=x_labels,
        y=y_labels,
        zmin=0.0,
        zmax=1.0,
        aspect="auto",
        color_continuous_scale="Viridis",
        title="Heatmap Interativo de Similaridade (Analogias)",
    )
    fig.update_layout(
        xaxis_title="Conceito B",
        yaxis_title="Conceito A",
        title_font_size=18,
    )
    fig.write_html(str(output_path))


def build_report(
    similarity: np.ndarray,
    items_a: Sequence[ConceptItem],
    items_b: Sequence[ConceptItem],
    top_k: int,
) -> Dict[str, Any]:
    flat = []
    for row in range(similarity.shape[0]):
        for col in range(similarity.shape[1]):
            flat.append((float(similarity[row, col]), row, col))
    flat.sort(reverse=True, key=lambda entry: entry[0])

    global_top = [
        {
            "score": score,
            "a": items_a[row].label,
            "b": items_b[col].label,
        }
        for score, row, col in flat[:top_k]
    ]

    per_row: Dict[str, List[Dict[str, Any]]] = {}
    for row in range(similarity.shape[0]):
        row_scores = [(float(similarity[row, col]), col) for col in range(similarity.shape[1])]
        row_scores.sort(reverse=True, key=lambda entry: entry[0])
        per_row[items_a[row].label] = [
            {"score": score, "b": items_b[col].label} for score, col in row_scores[:top_k]
        ]

    return {
        "shape": [int(similarity.shape[0]), int(similarity.shape[1])],
        "top_k": top_k,
        "global_top": global_top,
        "per_row_top": per_row,
    }


def load_items_from_paths(paths: Iterable[Path]) -> List[ConceptItem]:
    items: List[ConceptItem] = []
    for path in paths:
        data = load_json(path)
        prefix = f"{path.stem}/"
        items.extend(collect_items(data, label_prefix=prefix))
    return items


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("concept_a", type=Path)
    parser.add_argument("concept_b", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, default=Path("analogy_output"))
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--no-html", action="store_true")
    args = parser.parse_args()

    items_a = load_items_from_paths([args.concept_a])
    items_b = load_items_from_paths(args.concept_b)

    similarity = compute_similarity_matrix(items_a, items_b)

    args.out.mkdir(parents=True, exist_ok=True)
    png_path = args.out / "analogy_heatmap.png"
    html_path = args.out / "analogy_heatmap.html"
    report_path = args.out / "analogy_report.json"

    save_png_heatmap(similarity, [item.label for item in items_a], [item.label for item in items_b], png_path)
    if not args.no_html:
        save_plotly_heatmap(
            similarity,
            [item.label for item in items_a],
            [item.label for item in items_b],
            html_path,
        )

    report = build_report(similarity, items_a, items_b, top_k=args.top_k)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] PNG: {png_path}")
    if not args.no_html:
        print(f"[OK] HTML: {html_path}")
    print(f"[OK] REPORT: {report_path}")
    print("[TOP GLOBAL]")
    for match in report["global_top"]:
        print(f"  {match['score']:.3f}  {match['a']}  <->  {match['b']}")


if __name__ == "__main__":
    main()
