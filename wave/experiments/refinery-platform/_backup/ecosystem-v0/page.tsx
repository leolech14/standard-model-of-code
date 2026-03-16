'use client';

export default function EcosystemPage() {
  return (
    <div className="p-0 -m-6 h-[calc(100vh-0px)] overflow-hidden">
      <iframe
        src="/ecosystem-context-builder.html"
        className="w-full h-full border-0"
        title="Ecosystem Context Builder"
        allow="scripts"
      />
    </div>
  );
}
