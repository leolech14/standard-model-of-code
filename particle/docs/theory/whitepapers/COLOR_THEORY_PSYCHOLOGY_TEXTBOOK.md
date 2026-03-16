**COLOR THEORY,**

**GEOMETRY & INTELLIGENCE**

*From Light Physics to Production-Ready Color Intelligence Platforms*

**PART I** Perceptual Foundations · Color Psychology · Harmony Theory · Semantics

**PART II** Palettes as 3D Geometric Objects · Shape Analysis · Geometric Operations

**PART III** Variable Space · 13-Service Architecture · Advanced Mathematical Models

**PART IV** Canonical Schemas · Production Contracts · System KPIs · Integration

22 Chapters · 2 Appendices · 60 Glossary Terms

*Compiled & Edited for Design Systems Engineering*

**CHAPTER 1: THE THREE LAYERS OF COLOR THEORY**

\"Color theory\" is not a single discipline --- it is an **umbrella term spanning three distinct but interlocking layers**: physical, perceptual, and compositional. Conflating these layers is the most common source of confusion in design practice and the primary reason color advice can feel contradictory. This chapter establishes each layer with scientific precision.

**1.1 The Physical Layer: Light, Spectra, and Devices**

Color begins as electromagnetic radiation. The visible spectrum spans roughly 380--700 nm wavelengths, with each position corresponding to a perceived hue. However, color is not simply a property of a wavelength --- it is an interaction between spectral power distribution, a surface (or light source), and an observer.

+:--+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **KEY DEFINITION**                                                                                                                                                                                                                                                              |
|   |                                                                                                                                                                                                                                                                                 |
|   | Spectral Power Distribution (SPD): The relative power emitted or reflected at each wavelength. Two surfaces with different SPDs can look identical to a human observer (metamerism) while looking completely different to a camera or to a viewer under a different illuminant. |
+---+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  -----------------------------------------------------------------------
                       **DISPLAY TECHNOLOGY PRIMER**

  -----------------------------------------------------------------------

  ----------------------- ----------------------------------- ----------------- --------------------- ---------------------------------------------
      **Technology**                **Color Model**            **Mixing Type**    **Typical Gamut**              **Design Implication**

     LCD/OLED Monitor           RGB (Red, Green, Blue)            Additive            sRGB / P3        Bright colors lose detail at max saturation

   Inkjet / Offset Print   CMYK (Cyan, Magenta, Yellow, Key)     Subtractive       CMYK (smaller)       Saturated RGB colors cannot be reproduced

    Physical Materials         Reflected Spectral Power          Subtractive     Depends on pigment     Color shifts under different illuminants

    Wide-Gamut Displays            RGB (Display P3)               Additive       P3 \> sRGB by \~26%         Colors out-of-gamut for web CSS
  ----------------------- ----------------------------------- ----------------- --------------------- ---------------------------------------------

+:--+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **EDITOR\'S NOTE --- Why this matters for palette engines**                                                                                                                                                                                                                                                                                                      |
|   |                                                                                                                                                                                                                                                                                                                                                                  |
|   | Any palette engine that operates purely on hex values is operating on device-specific, non-perceptual numbers. Hex values are output values for sRGB displays. As soon as your palette is displayed on a wide-gamut device or printed, the same hex will look different. Build internal representations in device-independent perceptual spaces (see Chapter 2). |
+---+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**1.2 The Perceptual Layer: Eyes, Brain, and Opponent Channels**

Human color vision arises from three types of cone photoreceptors (L, M, S --- roughly long, medium, and short wavelength), whose signals are recombined by retinal and cortical processing into three perceptual channels:

- Luminance channel (light--dark)

- Red--Green opponent channel

- Yellow--Blue opponent channel

These channels are non-independent: what the brain perceives as \'this color\' depends on surrounding colors, adaptation state, spatial context, and illuminant estimation. This gives rise to phenomena critical for palette design:

  --------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------
           **Phenomenon**                                                                          **What Happens**                                                                                                                **Design Consequence**

        Chromatic Adaptation         The visual system adjusts its sensitivity to the dominant illuminant, making \'white\' perceptually stable under very different light sources   A brand color will look different on a warm-lit vs cool-lit print, or between monitors with different white points

        Simultaneous Contrast                         A neutral color placed next to a saturated hue appears shifted toward the complementary hue of the neighbor                         Two \'identical\' grays in different contexts can look completely different --- palette screenshots lie

   Assimilation (Spreading Effect)                            In small/fine patterns, a color shifts toward neighbors (opposite of simultaneous contrast)                                     Fine texture in UI can make colors appear to blend --- affects readability of small UI elements

             Mach Bands                                         The visual system exaggerates luminance edges, creating perceived bands at transitions                                      Gradients can appear striped even if the underlying data is smooth --- critical for gradient design

             Hunt Effect                                                           Colors appear more saturated at higher luminance                                                         Dark-mode palettes require recalibration --- the same hue at lower lightness reads as less saturated
  --------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------

**1.3 The Compositional Layer: Relationships and Roles**

This is the layer most associated with \'color theory\' in design education: color wheels, harmony types, contrast relationships, and hierarchy. These are not physical laws --- they are engineering heuristics that work because they manipulate the perceptual mechanisms described in §1.2.

**Important editorial clarification:** complementary harmony is not a law of nature. It works because it creates maximum hue-angle contrast in color space, which the opponent-channel visual system finds stimulating. If you understand the perceptual mechanism, you can break rules intelligently.

+:--+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **THREE-LAYER DESIGN PRINCIPLE**                                                                                                                                                                                                                                                                                                          |
|   |                                                                                                                                                                                                                                                                                                                                           |
|   | Always identify which layer a design problem lives in before solving it. \'This color looks wrong on dark background\' is a perceptual problem (simultaneous contrast). \'This palette feels chaotic\' is a compositional problem (harmony/proportion). \'This print doesn\'t match my screen\' is a physical problem (gamut/illuminant). |
+---+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**CHAPTER 2: PERCEPTUAL COLOR SPACES --- THE ENGINEER\'S MAP**

Not all color spaces are created equal. The choice of color space determines what operations are perceptually meaningful --- and which will produce distorted results. This chapter is your engineering reference for choosing the right space for each task.

**2.1 The Problem with RGB and HSL**

RGB (and its derivative HSL/HSV) is a device encoding standard, not a perceptual model. Equal numerical steps in RGB do not correspond to equal perceived changes in color.

- A 10% lightness step in HSL near mid-gray may be barely visible; the same step near black or white is dramatic

- Gradient interpolation in RGB often produces muddy, perceptually uneven transitions (the infamous \'dark band\' through orange when interpolating red→yellow)

- Saturation in HSL is not perceptual saturation --- a highly saturated yellow and a highly saturated purple at the same HSL saturation look nothing alike in perceived vividness

**2.2 CIE Color Spaces: Toward Perceptual Uniformity**

The International Commission on Illumination (CIE) has developed several models attempting to standardize perceptual measurements. Understanding their evolution reveals why newer spaces are superior.

  ------------------------ ---------- ----------------------------------------------------- --------------------------- ---------------------------------------------------------------------- ----------------------------------------------------------------------
         **Space**          **Year**                     **Dimensions**                      **Perceptual Uniformity**                            **Best Used For**                                                      **Key Limitation**

          CIE XYZ             1931                           X, Y, Z                                   None              Reference/conversion hub --- every other space converts through XYZ    Not perceptually uniform --- doesn\'t correspond to human experience

   CIE L\*a\*b\* (CIELAB)     1976     L\* (lightness), a\* (red-green), b\* (yellow-blue)             Good                  Color difference calculation, print workflows, WCAG contrast         Still imperfect --- hue uniformity is poor, blues are distorted

     CIE L\*C\*h (LCH)        1976        L\* (lightness), C\* (chroma), h° (hue angle)                Good                         Intuitive editing --- like HSL but perceptual                                    Same limitations as CIELAB

          CIECAM02            2002             J (lightness), C (chroma), h (hue)                    Very Good                   Complex appearance modeling with surround/illuminant                 Complex to implement; overkill for most palette engines

           Oklab              2020        L (lightness), a (green-red), b (blue-yellow)              Excellent                         Gradient interpolation, palette editing                               Relatively new --- not in all software yet

           OkLCH              2020          L (lightness), C (chroma), h (hue angle)                 Excellent           Human-friendly editing in perceptual space; best for palette engines                 Same as Oklab --- limited legacy support
  ------------------------ ---------- ----------------------------------------------------- --------------------------- ---------------------------------------------------------------------- ----------------------------------------------------------------------

**2.3 The Oklab / OkLCH Recommendation**

+:--+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **ENGINE RECOMMENDATION**                                                                                                                                                                                                                                           |
|   |                                                                                                                                                                                                                                                                     |
|   | For any new color palette engine: store and compute internally in OkLCH. Convert to sRGB hex only for output. This single decision eliminates most gradient banding issues and makes semantic features like \'increase chroma by 15%\' actually mean what they say. |
+---+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

OkLCH uses three intuitive axes perfectly aligned with the psychological properties that drive color emotion (see Chapter 3):

  ----------------- --------------------------------- ----------------------------------------------- --------------------------------------------------------------
   **OkLCH Axis**               **Range**                         **Perceptual Meaning**                     **Psychological Effect (Preview --- see Ch. 3)**

   L --- Lightness        0 (black) → 1 (white)          Perceived luminance, uniform across hues        Higher L → higher pleasure; complex arousal relationship

    C --- Chroma     0 (achromatic) → \~0.4+ (vivid)        Perceived colorfulness / saturation                  Higher C → higher arousal, higher energy

   h --- Hue Angle              0° → 360°              Perceived hue (0°=red, 120°=green, 240°=blue)   Context-dependent; warm vs cool axis centered \~30° / \~210°
  ----------------- --------------------------------- ----------------------------------------------- --------------------------------------------------------------

**2.4 Color Difference Metrics**

Measuring \'how different\' two colors are requires a perceptual metric. Different metrics serve different purposes:

  --------------------- -------------------------------------------- ----------------------------------------------------------------------- --------------------------------------------------------
       **Metric**                    **Formula Basis**                                            **Use Case**                                                **Typical Threshold**

      ΔE76 (CIE76)              Euclidean distance in CIELAB                              Quick approximate comparison                          ΔE \< 2: colors appear identical to most observers

          ΔE94                        Weighted CIELAB                                        Graphic arts comparison                          More accurate than CIE76 for industrial color matching

    CIEDE2000 (ΔE00)     Complex weighted formula with hue rotation                   Gold standard for perceptual accuracy                           ΔE00 \< 1: virtually indistinguishable

     Oklab Euclidean            √(ΔL² + Δa² + Δb²) in Oklab           Palette engine distance --- computationally simple, perceptually good            \~0.1 for just-noticeable difference

   WCAG Contrast Ratio           Relative luminance formula                     Accessibility --- text legibility on backgrounds                    4.5:1 for normal text; 3:1 for large text
  --------------------- -------------------------------------------- ----------------------------------------------------------------------- --------------------------------------------------------

**2.5 Diagram: Color Space Hierarchy**

  -------------------- ----------------------------- --------------------------------- ---------------------------------
       **Layer**                 **Space**                  **Operation Type**                **Convert To/From**

    Output / Device         sRGB (Hex, #RRGGBB)            Storage, web display             ↓ Linearize gamma → XYZ

     Reference Hub                CIE XYZ                   Conversion gateway               ↔ To any other space

   Perceptual Classic          CIELAB / LCH                ΔE calculation, WCAG            ← XYZ via D65 white point

   Perceptual Modern    Oklab / OkLCH ✓ RECOMMENDED   Engine math, gradients, editing   ← XYZ (simple linear transform)
  -------------------- ----------------------------- --------------------------------- ---------------------------------

**CHAPTER 3: THE PSYCHOLOGY OF COLOR --- WHAT THE EVIDENCE ACTUALLY SAYS**

Color psychology is among the most misrepresented topics in design. Categorical claims like \'red increases appetite\' or \'blue conveys trust\' circulate as facts. This chapter separates robust findings from marketing myths by examining the actual experimental evidence.

+:--+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **CRITICAL FRAMING**                                                                                                                                                                                                                                                                                                                                                                       |
|   |                                                                                                                                                                                                                                                                                                                                                                                            |
|   | The single most defensible statement in color psychology: colors can carry meaning and influence affect, cognition, and behavior --- but effects are typically context-dependent, not universal laws. The strength of any color effect depends on learned associations, motivational context, culture, individual differences, and how color properties (hue, lightness, chroma) interact. |
+---+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**3.1 The Pleasure--Arousal--Dominance (PAD) Framework**

The most empirically grounded model for color-emotion relationships uses the three-dimensional PAD space, originally from environmental psychology and applied to color by Valdez & Mehrabian (1994). This is your primary engineering model.

  -------------------- ------------------------------------------------------ ----------------------------------------------- ---------------------------------------------------------------
   **PAD Dimension**                    **What It Measures**                   **Color Predictors (Most to Least Powerful)**                      **Direction of Effect**

   Pleasure (Valence)     How positive / pleasant the color experience is        Brightness (L) \> Saturation (C) \>\> Hue     Higher L → More Pleasant; Higher C → More Pleasant (moderate)

        Arousal         How activating / stimulating the color experience is         Saturation (C) \> Brightness (L)               Higher C → More Arousing; Higher L → LESS Arousing

       Dominance         How in-control / powerful the color makes one feel          Brightness (L) \> Saturation (C)               Higher L → Less Dominant; Higher C → More Dominant
  -------------------- ------------------------------------------------------ ----------------------------------------------- ---------------------------------------------------------------

+:--+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **ENGINEERING INSIGHT**                                                                                                                                                                                                                                                                                                              |
|   |                                                                                                                                                                                                                                                                                                                                      |
|   | Notice that hue is the WEAKEST predictor of emotional tone in controlled studies. Lightness and saturation dominate. This means: to move a palette toward \'calmer,\' reduce chroma. To move toward \'more energetic,\' increase chroma and introduce higher contrast. Hue adjustments alone will have the weakest emotional effect. |
+---+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**PAD Model: Relative Strength of Predictors (Pleasure Dimension)**

+---------------:+---------------------------------------------------------+--------+
| Brightness (L) |   --------------------------------------------- ------  | **87** |
|                |                                                         |        |
|                |                                                         |        |
|                |   --------------------------------------------- ------  |        |
+----------------+---------------------------------------------------------+--------+
| Saturation (C) |   ---------------------------- -----------------------  | **54** |
|                |                                                         |        |
|                |                                                         |        |
|                |   ---------------------------- -----------------------  |        |
+----------------+---------------------------------------------------------+--------+
| Hue (h°)       |   ------------ ---------------------------------------- | **23** |
|                |                                                         |        |
|                |                                                         |        |
|                |   ------------ ---------------------------------------- |        |
+----------------+---------------------------------------------------------+--------+

Note: Values are illustrative relative weights based on Valdez & Mehrabian (1994) --- Pleasure dimension. Actual regression weights vary by study.

**PAD Model: Relative Strength of Predictors (Arousal Dimension)**

+---------------:+--------------------------------------------------------+--------+
| Saturation (C) |   --------------------------------------------- ------ | **91** |
|                |                                                        |        |
|                |                                                        |        |
|                |   --------------------------------------------- ------ |        |
+----------------+--------------------------------------------------------+--------+
| Brightness (L) |   ------------------------------ --------------------- | **61** |
|                |                                                        |        |
|                |                                                        |        |
|                |   ------------------------------ --------------------- |        |
+----------------+--------------------------------------------------------+--------+
| Hue (h°)       |   --------- ------------------------------------------ | **19** |
|                |                                                        |        |
|                |                                                        |        |
|                |   --------- ------------------------------------------ |        |
+----------------+--------------------------------------------------------+--------+

Note: Higher Saturation drives Arousal more strongly than Brightness; effect of Hue is comparatively small.

**3.2 Hue-Specific Effects: What\'s Real vs Mythology**

Despite the primacy of lightness and saturation in general models, some hue-specific effects have genuine experimental support --- but they are consistently context-dependent.

  ----------------- ------------------------------------------------------------------------------ ------------------------------ ------------------------------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------
       **Hue**                                    **Claimed Effect**                                    **Evidence Quality**                                          **Mechanism**                                                                                                   **Critical Context Dependency**

     Red (\~0°)      Impairs performance on achievement tasks; increases appetite; signals danger   Moderate (replication mixed)     Avoidance motivation activation; learned cultural association with danger/stop         Effect is specific to achievement contexts (tests, tasks). In attraction contexts, red increases attractiveness ratings. Effect reversal is common.

    Blue (\~240°)                Increases creative performance; calming; trustworthy                     Weak to moderate                Possibly approach motivation (openness); cool temperature association          Creative effects are contested and difficult to replicate. \'Trustworthy\' may be a cultural/category association (banks, hospitals) not a direct effect.

   Green (\~140°)                   Restful; eco-associated; health/safety signal                               Weak                                  Ecological association (natural environments)                                                  Strongest for brand/category contexts. Difficult to isolate from lightness/saturation confounds.

   Yellow (\~80°)                    Attention-grabbing; cheerful; caution signal                      Moderate for attention      High spectral sensitivity of the eye at yellow wavelengths; cultural caution signal                                   Attention effect may be primarily a luminance/contrast artifact, not a hue effect per se.

   Orange (\~30°)                        Energy; warmth; appetite stimulation                           Weak direct evidence          Likely secondary association to food/fire; combination of red+yellow effects                                      Frequently confounded with saturation --- \'energetic orange\' is also high-chroma orange.

   Purple (\~280°)                           Luxury; royalty; creativity                              Weak --- mostly cultural                Historical scarcity of purple dye creating luxury association                                            Highly culture-specific; not universal. Modern associations vary significantly by generation.
  ----------------- ------------------------------------------------------------------------------ ------------------------------ ------------------------------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------

**3.3 Cross-Cultural Reality**

Large-scale international research reveals a nuanced picture: there are some statistical universals, but significant variation exists between cultures, and no single color has a universal meaning.

**Color--Emotion Cross-Cultural Pattern (Simplification of Jonauskaite et al. 2020, 30 countries)**

  ------------- ------------------- -------------------- -------------------- -------------------- ------------------- -------------------
                    **Yellow**            **Blue**          **Black/Dark**       **Gray/Blue**           **Red**        **Brown/Yellow**

  **Joy**        Strong Universal     Strong Universal    Moderate Universal   Moderate Variable    Moderate Variable     Weak Variable

  **Trust**      Moderate Variable   Moderate Universal        Variable             Variable            Variable            Variable

  **Fear**           Variable             Variable         Strong Universal    Moderate Universal       Variable        Moderate Variable

  **Sadness**        Variable             Variable             Moderate         Strong Universal        Variable            Variable

  **Anger**          Variable             Variable             Moderate             Variable        Strong Universal        Moderate

  **Disgust**        Variable             Variable             Variable             Variable            Moderate        Strong Universal
  ------------- ------------------- -------------------- -------------------- -------------------- ------------------- -------------------

Legend: Green = Strong cross-cultural agreement; Blue = Moderate universal; Neutral = Variable by culture

+:--+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **DESIGN SYSTEMS IMPLICATION**                                                                                                                                                                                                                                                                           |
|   |                                                                                                                                                                                                                                                                                                          |
|   | Any semantic palette engine should parameterize by locale and domain, not assume universal meaning. \'Trustworthy blue\' in Western healthcare may be \'medical sterility\' in one culture and \'cold distance\' in another. Build meaning(palette \| context, locale) --- never meaning(palette) alone. |
+---+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**3.4 Individual Differences and Preference**

Color preference varies systematically across individuals:

- The \'universal preference for blue\' is real but not absolute --- it holds as a group average but shows significant individual spread

- Color preferences correlate with personality traits (e.g., openness to experience and preference for complex/diverse palettes)

- Ecological Valence Theory (Palmer & Schloss, 2010) proposes that preference for a color tracks the average valence of objects associated with that color --- a strong, concrete hypothesis

- Age affects preference: older adults tend to prefer lower-saturation, lighter colors

- Context shifts preference: the \'best\' color for a car differs from the best for a food product

**CHAPTER 4: COMBINATION EFFECTS --- WHY PALETTES ARE NOT SUMS OF THEIR PARTS**

A palette is not the sum of N individual color meanings. The perceptual and semantic effects of a color change fundamentally depending on which other colors surround it, what role it plays, and at what proportion it appears. This chapter covers the science of combination effects.

**4.1 Role and Proportion Transform Meaning**

The same blue can mean completely different things depending on its role:

  -------------------------------- -------------------------------------------- -------------------------------------- -----------------------------------------------------------------------------------------------
              **Role**              **Same Blue Hue (h≈240°, C=0.18, L=0.55)**           **Semantic Reading**                                               **Perceptual Effect**

        Full-page background               Dominant --- immersive field           Calm, corporate, cool, distancing          Maximum adaptation; eye adjusts white point toward blue; everything else looks warm

    Primary CTA button on white              Small accent on neutral               Active, interactive, trustworthy               High contrast pops; red-green opponent channel activated; draws attention

           Text on white                     High-contrast typography                Clear, neutral, professional            Primarily contrast effect --- blue text on white is readable but colder than black

   Subtle border/divider on white           Very low prominence accent                   Structural, minimal                                Almost invisible as color; primarily a luminance edge

     Error state (red context)                Competing warm vs cool             Confusing --- contradicts convention   Simultaneous contrast with red surroundings makes blue look more vivid --- amplifies conflict
  -------------------------------- -------------------------------------------- -------------------------------------- -----------------------------------------------------------------------------------------------

+:--+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **ENGINE RULE #1**                                                                                                                                                                                                                                                                  |
|   |                                                                                                                                                                                                                                                                                     |
|   | A palette engine must model colors with their roles and proportions, not as isolated swatches. The data structure must include: { swatch, role, weight/proportion, adjacency }. Computing semantics on isolated hex values without role context will produce incorrect predictions. |
+---+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**4.2 Harmony Mechanisms: What Makes Combinations Feel Coherent**

Harmony is the subjective sense that colors \'go together.\' Experimental aesthetics has identified several quantitative predictors:

  ------------------------------------ -------------------------------------------------------------------------------------- ---------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------
         **Harmony Principle**                                             **Mechanism**                                                     **Effect on Harmony Score**                                                                    **Practical Implication**

             Hue Similarity             Colors with closer hue angles (analogous) share opponent channel activation patterns              Increases harmony (all else equal)                                         Analogous palettes are baseline harmonious --- good for low-conflict UI

   Lightness Contrast (figure-ground)          High L contrast between adjacent roles (text on bg, button on surface)             Increases preference for figure color specifically                                        Make your CTA high-contrast with its immediate background

         Saturation Congruence                   Similar chroma levels across swatches create perceptual coherence                                Increases harmony                       Mixing a highly saturated accent with desaturated neutrals is fine --- but mixing multiple high-saturation hues feels chaotic

         Complementary Tension                       Opposite hues create maximum opponent-channel stimulation                 Polarizing: can increase energy/attention or feel garish                          Use complementary pairs as accent-to-CTA relationships, not as dominant colors

       Order / Gradient Structure         Colors that form a perceivable progression (hue, lightness, or temperature ramp)        Increases harmony --- sequential logic is readable                                     Monochromatic and analogous progressions exploit this strongest
  ------------------------------------ -------------------------------------------------------------------------------------- ---------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------

**4.3 Semantic Interaction: How Color Combinations Shift Meaning**

Combinations do not just modulate aesthetic harmony --- they shift semantic meaning. Some documented interaction patterns:

**Semantic Interaction Matrix: Adding a Second Color to a Base**

  ------------------------ -------------------------- ----------------------- --------------------------- ---------------------- -----------------------
                                  **+ Black**               **+ White**            **+ Gold/Yellow**         **+ Red (\~0°)**        **+ Cool Gray**

  **Blue base**             Luxury, authority, depth    Clean, open, modern        Heritage, warmth        Power, high tension     Professional, calm

  **Cream/Neutral base**    Pure, minimal, clinical        Soft, gentle          Festive, warm welcome      High-energy, bold       Soft professional

  **Red base**                 Premium, exclusive       Bold, approachable     Danger, urgency (doubles)   Intensity, full heat      Action, sporty

  **Green base**               Corporate, serious      Fresh, health-forward     Earth tones, organic        Nature + action      Calm nature, wellness
  ------------------------ -------------------------- ----------------------- --------------------------- ---------------------- -----------------------

**4.4 Quantitative Models for Palette Harmony**

Several researchers have proposed models that score palette harmony quantitatively:

- Schloss & Palmer (2011): Pair harmony is predicted by component preference + lightness contrast. Formula: Harmony(A,B) ≈ w1·Pref(A) + w2·Pref(B) + w3·ΔL(A,B)

- Ou et al. (2004): Two-color combination emotion scales (warm-cool, heavy-light, active-passive) modeled from L, C, h of both colors

- O\'Donovan et al. (2011): Learned compatibility scores from millions of Adobe Kuler themes --- large-dataset approach showing that data-driven models outperform rule-based ones

+:--+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **EDITOR\'S SYNTHESIS**                                                                                                                                                                                                                                                                                                                          |
|   |                                                                                                                                                                                                                                                                                                                                                  |
|   | Rule-based harmony models (Itten\'s color wheel, complementary/triadic rules) capture real perceptual regularities but fail on edge cases. Data-driven models generalize better. The ideal engine combines both: a rule-based layer for constraints (WCAG, CVD safety) and a data-driven layer for compatibility scoring and semantic inference. |
+---+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**CHAPTER 5: GRADIENT SCIENCE --- CONTINUOUS COMBINATIONS**

Gradients are palettes distributed continuously across space. They carry unique semantic qualities (depth, atmosphere, modernity, dynamism) but are also uniquely vulnerable to perceptual artifacts. Mastering gradient science requires understanding both the visual system and interpolation mathematics.

**5.1 Why Gradients Are Perceptually Special**

A gradient is not just \'one color fading into another.\' It is a spatially structured stimulus that engages the visual system\'s edge-detection mechanisms:

- The visual system is not a linear recorder. It emphasizes changes in luminance (Mach band effect), which means a mathematically smooth gradient can appear to have visible bands at certain luminance transition speeds

- Gradients create strong depth cues (atmospheric haze, volumetric light) when lightness decreases away from a notional light source

- Color temperature gradients (warm-to-cool) create spatial and atmospheric effects used in painting since the Renaissance (\'sfumato\')

**5.2 The Interpolation Space Problem**

The most important technical decision for gradient quality is the interpolation color space. Equal numeric steps in different spaces create perceptually unequal perceptual steps:

  ------------------------- ------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------- ------------------------------------------------ --------------------
   **Interpolation Space**                                                    **Typical Artifact**                                                                                               **Why It Happens**                                                            **Best Used When**                 **Quality Rating**

         sRGB (Hex)                               \'Dark band\' through warm midpoints, e.g., red→green goes through near-black                              Gamma encoding creates non-linear perceptual steps; midpoint lands in dark perceptual zone                    Legacy compatibility only                    ★★☆☆☆

         Linear RGB                        Better than sRGB but hue shifts still occur; orange→blue creates unexpected gray midpoints                                    Linear but not perceptual --- equal energy is not equal perception                      Color mixing in rendering (physically correct)         ★★★☆☆

           HSL/HSV           Hue shifts follow shortest path on HSL wheel, often through perceptually unexpected intermediate hues; uneven lightness                  Hue angle arithmetic ignores perceptual non-uniformity of the hue circle                         Quick prototyping, not production                ★★☆☆☆

         CIELAB/LCH                                        Hue chroma can dip at midpoints; \'hue shift\' on long arcs                                                        Chroma can become zero if L paths cross achromatic region                                 Scientific visualization, print                 ★★★★☆

     Oklab (Recommended)                      Minimal artifacts; perceptually smooth lightness progression; correct midpoint colors                    Oklab has excellent perceptual uniformity including for hue; designed specifically for smooth gradients    All UI/web gradients, palette interpolation           ★★★★★
  ------------------------- ------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------- ------------------------------------------------ --------------------

**5.3 Gradient Semantic Taxonomy**

Gradients carry specific semantic associations that should be tracked in a palette engine:

  --------------------------------------- --------------------------------------------------------------- ------------------------------------------------------------------------ ------------------------------------------------------------
             **Gradient Type**                               **Perceptual Properties**                                           **Semantic Associations**                                          **UI/Design Applications**

       Light → Dark (Luminance Ramp)                    Smooth L decrease; zero C variation                                Depth, shadow, night, privacy, premium                            Backgrounds, cards, dark-mode atmosphere

         Warm → Cool (Temperature)         Hue angle shift from \~30° to \~220°; can maintain constant L   Transition, time-of-day (sunset/dusk), emotional shift, transformation        Hero backgrounds, state transitions, data ranges

   Saturated → Desaturated (Chroma Ramp)             C decreases toward gray; L and h constant                              Fading, memory, mist, soft elegance                                Overlay gradients, fade-out effects

            Vibrant Multi-Stop                     Multiple high-C hue transitions through Oklab                Modernity, energy, digital-native, generative art aesthetic               App brand gradients, synthwave/holographic UI

       Subtle Tonal (Monochromatic)                     Same hue; slight L and C variation                                   Refinement, luxury, minimal polish                     Button states, surface elevation in Material-style systems

       Diverging (Neutral Midpoint)               Two hues diverge from neutral gray/white center                         Balance, comparison, deviation from norm                      Data visualization, heat maps, progress indicators
  --------------------------------------- --------------------------------------------------------------- ------------------------------------------------------------------------ ------------------------------------------------------------

**5.4 Gradient Quality Checklist**

+:--+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **PRODUCTION CHECKLIST**                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|   | Before shipping a gradient: (1) Verify lightness L in OkLCH is monotonic if \'smooth\' is the intent --- use a lightness plot. (2) Check midpoint hue for unexpected shifts. (3) Simulate under deuteranopia/protanopia --- gradients often become invisible to CVD users. (4) Check Mach band artifacts at specific lightness transition rates --- if the band looks exaggerated, smooth the L curve. (5) Verify WCAG contrast at the worst-contrast point if text overlays the gradient. |
+---+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**CHAPTER 6: PALETTE TOPOLOGIES --- THE STRUCTURAL GRAMMAR OF COLOR SYSTEMS**

A palette topology describes how colors relate to each other structurally --- in hue space, lightness space, and role space. Understanding topology lets you diagnose and design palettes systematically rather than intuitively.

**6.1 Harmony-Based Topologies (Aesthetic Coherence)**

These topologies are defined by the angular relationships between swatches on the hue circle:

  --------------------- -------------------------------------- ------------------------------------------------------------ --------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------
      **Topology**                  **Hue Angles**                                **OkLCH Description**                                                           **Semantic Signature**                                                                                     **Risk & Best Practice**

      Monochromatic                Single hue ±10°              Single h°; vary L (0.2--0.9) and C (0--max) systematically                  Coherent, focused, minimal, elegant, depth through luminance alone                        Risk: monotony without sufficient L contrast. Fix: ensure at least 0.4 ΔL between darkest and lightest.

        Analogous              3--5 hues within 60° arc                  Hue range of ≤60°; moderate C variation                            Natural, organic, calm, narrative (suggests movement or transition)                   Risk: low contrast, figures blend into backgrounds. Fix: use L contrast for role separation, not hue contrast.

      Complementary              2 hues \~180° apart                 h° and h°+180°; typically 1 dominant + 1 accent            High tension, energy, sports/action, attention-grabbing; can read as dynamic or aggressive                Risk: visual vibration if both at high C. Fix: desaturate one hue or use 80/20 proportion rule.

   Split Complementary   1 base + 2 flanking (\~150°, \~210°)           One dominant; two near-complement accents            Energy without full tension; balanced excitement; more complex visual interest than complementary                    Safer than pure complementary. Dominant hue should own 60-70% of visual weight.

         Triadic               3 hues at 120° intervals                    h°, h°+120°, h°+240°; equal spacing                          Vibrant, playful, children\'s content, illustration; challenging to balance              Risk: chaotic if all three at equal weight and saturation. Fix: one dominant, one secondary at 50% C, one accent.

    Tetradic / Square          4 hues at 90° intervals                         Complex; 4 hue anchor points                                          Rich, complex, celebratory; fashion/art contexts                               Risk: most complex to manage. Fix: strict proportion control --- one dominant, one secondary, two accents.
  --------------------- -------------------------------------- ------------------------------------------------------------ --------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------

**6.2 Functional Topologies (Role-Based Palettes)**

In design systems and products, palette topology is defined by function, not by hue angle:

  --------------------------- --------------------------------------------------------------- ------------------------------------------------------------------------------ -------------------------------------------------------------------------------------------
         **Topology**                                  **Structure**                                                         **Token Roles**                                                                 **Semantic Design Intent**

       Neutral + Accent        1 dominant neutral family (N tints/shades) + 1--2 accent hues   surface, surface-variant, on-surface, primary, primary-container, secondary     Maximum hierarchy clarity; accent carries brand and interaction; neutrals carry layout

         Brand System              Primary brand hue + extended family + semantic tokens       primary, secondary, tertiary, error, warning, success, info + surface tokens         Full design system palette; needed for products with complex state management

   Editorial / Art Direction     Curated palette chosen for mood, not systematic function               Variable --- may have background, accent, text, decorative                   Emotional impact and brand voice; less concerned with reusable token logic

      Data Visualization              Sequential, diverging, or qualitative families                   data-low, data-mid, data-high; category-1 through category-N              Perceptual accuracy; equal visual weight per data dimension; CVD safety is critical

    Accessible / Inclusive       All role pairs meet WCAG AA or AAA; CVD-safe hue choices           Same as Brand System but constrained by accessibility requirements        Legal compliance + inclusive design; often requires sacrificing some aesthetic preference
  --------------------------- --------------------------------------------------------------- ------------------------------------------------------------------------------ -------------------------------------------------------------------------------------------

**6.3 Data Visualization Palette Topology (Special Case)**

Data visualization palettes follow different design rules than UI palettes --- perceptual accuracy is paramount:

  --------------------------- ------------------------------------------------------------ --------------------------------------------------- --------------------------------------------------------------------------- -------------------------------------------------------------------
      **DV Palette Type**                            **Structure**                                           **L Behavior**                                                 **Hue Behavior**                                                       **Best Data Type**

          Sequential           Single hue + lightness ramp, OR hue-shift with monotonic L   Monotonically decreasing L (light=low, dark=high)        Constant or small shift toward higher chroma hue at high values               Ordered/magnitude data: density, temperature, count

           Diverging                   Two hues diverging from a neutral midpoint             Symmetric around midpoint (midpoint = max L)        Two hues, one per wing, diverging in h° away from near-neutral center     Deviation from baseline, positive/negative, above/below threshold

   Qualitative / Categorical            N hues with equal perceptual prominence                 Matched L and C across all hues in OkLCH        Maximum hue discrimination: spread across hue circle, avoid adjacent hues        Categorical data: groups, clusters, nominal categories

            Cyclic                Loop-safe: endpoint matches start point perceptually       Symmetric --- L rises then falls (or constant)                    Full 360° hue rotation returning to origin                     Circular/periodic data: compass direction, time-of-day, phase
  --------------------------- ------------------------------------------------------------ --------------------------------------------------- --------------------------------------------------------------------------- -------------------------------------------------------------------

**CHAPTER 7: THE SCIENCE OF COLOR SEMANTICS**

\'Semantics\' in the context of color means the meanings, associations, and conceptual content that colors carry. This chapter covers the theoretical frameworks you need to formally model color meaning --- a prerequisite for any semantic palette engine.

**7.1 Five Explanatory Frameworks for Color Meaning**

  --------------------------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------ ----------------------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------
            **Framework**                                                                                  **Core Claim**                                                                                                                           **Evidence Base**                                                                                          **Encodability in Engine**

   Ecological Valence Theory (EVT)   Color preference tracks the average affective valence of objects associated with that color (e.g., blue is liked because sky, clean water, etc. are liked)      Strong --- quantitative model with object-color association data; explains \~80% of variance in hue preference               HIGH --- build object-color association lexicon; compute mean valence of associations

           Color-as-Signal                Colors function as evolutionary or learned signals (red=danger/blood, green=fresh food, etc.); trigger motivational states in specific contexts         Moderate --- specific effects (red impairs achievement) replicate moderately; general signal theory is well-supported                 MEDIUM --- requires context tagging; signal effects are context-specific

    Cultural / Linguistic Shaping     Color meanings are partly constructed by language and cultural experience (e.g., languages with fewer basic color terms differ in color discrimination)                                 Strong for variation; moderate for universals (Berlin & Kay)                                       MEDIUM --- requires locale parameter; cross-cultural data from large studies available

      Crossmodal Correspondence                   Color systematically maps to other sensory dimensions: taste (sweet↔pink), smell, shape (angular↔red), music (high pitch↔bright)                                                Moderate --- laboratory robust but effect sizes vary                                    HIGH for specific domains (food, fragrance, audio branding) --- add modality-specific semantic layers

        Cognitive / Symbolic                      Colors carry meaning through learned category membership: red=error in UI, green=success, yellow=caution in industrial contexts                                           Very strong in specific domains --- deeply ingrained conventions                                            HIGH for domain-specific engines --- encode convention tables per domain
  --------------------------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------ ----------------------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------

**7.2 The Semantic Space Model**

To compute with color meaning, you need a formal semantic representation. We recommend a multi-layer model:

  ------------------------------ -------------------------------------------------------------- ------------------------------------------------------------------------ ---------------------------------------------------------------------------- -----------------------------------------------------------------------
        **Semantic Layer**                             **Representation**                                                  **Range / Values**                                                        **How to Populate**                                                   **Cross-Cultural Stability**

   Dimensional Affect (PAD/VAD)       3D continuous vector \[Valence, Arousal, Dominance\]                             Each dimension: \[-1, +1\]                         Regression from L, C, h using literature priors; refine with human ratings        HIGH --- VAD is language-universal; robust across cultures

       Adjective Embedding        High-dimensional learned vector; decoder to adjective labels             Adjective set: domain-dependent (\~50--200 labels)               Train on tagged palette datasets (Kuler, COLOURlovers, custom ratings)     MEDIUM --- adjective meanings vary culturally; parameterize by locale

       Category/Domain Tags             One-hot or multi-hot vector of domain categories         e.g., \[tech, health, luxury, food, sport, children, corporate, \...\]                 Manual encoding + category-trained classifier                     LOW --- highly domain and culture specific; must be parametric

     Crossmodal Associations                      Per-modality feature vectors                           e.g., sweetness \[0,1\], texture rough/smooth \[-1,1\]             Encode from established crossmodal literature; food/fragrance-specific             MEDIUM --- some universals; cultural shaping present

       Conventional Signals             Rule table: context + hue range → signal meaning                       e.g., UI: red ∈ \[0°, 20°\] → error/danger                               Hard-coded per domain; updateable rule tables                            DOMAIN-SPECIFIC --- encode per-domain, per-locale
  ------------------------------ -------------------------------------------------------------- ------------------------------------------------------------------------ ---------------------------------------------------------------------------- -----------------------------------------------------------------------

**7.3 The Semantic Invariant Problem**

A central engineering challenge for palette systems: when you generate a variant (dark mode, seasonal theme, accessible version), how do you ensure the variant preserves the original semantic intent?

This is the \'semantic invariant\' problem: what properties of a palette must remain constant across a transformation to preserve meaning?

  ------------------------------- ------------------------------------------------------------------------ ------------------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------
      **Transformation Type**                                 **What Changes**                                                   **What Must Remain Constant for Semantic Invariance**                                                    **OkLCH Engineering Approach**

       Dark Mode Adaptation        Background L decreases dramatically (0.95→0.08); surface colors invert             VAD valence/arousal relative balance; hue associations; brand hue identity              Maintain same h° and C for brand hues; adjust L to maintain equivalent contrast ratios

       Accessible Adjustment          Some hue/lightness values adjusted to meet WCAG contrast ratios       Semantic category membership (success=green, error=red must remain); relative harmony structure    Use OkLCH constraints: fix h°, adjust L until contrast passes; avoid large C changes

   Seasonal / Contextual Variant       Accent hues shifted (e.g., warm winter palette vs cool summer)                      Brand identity; primary action color hierarchy; harmony topology                           Shift h° within ±30° of base; maintain relative C and L relationships

        Tonal / Brand Scale                   Systematic generation of tones from brand color                                       Primary brand color identity at key tone stops                              Fix h°, linearly interpolate L from 0.1 to 0.95 in OkLCH; allow C to peak at mid-L
  ------------------------------- ------------------------------------------------------------------------ ------------------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------

**CHAPTER 8: BLUEPRINT --- THE SEMANTIC PALETTE ENGINE**

This chapter consolidates all prior theory into a concrete, buildable architecture for a semantic color palette engine --- a system that generates, evaluates, and transforms palettes while tracking semantic meaning across all operations.

**8.1 System Architecture Overview**

  ----------- ----------------------- ------------------------------------------------------------------------ ----------------------------------------------
   **Layer**         **Name**                                    **Responsibility**                                            **Tech Stack**

       0          IO & Conversion                   HEX ↔ sRGB ↔ OkLCH conversion; gamut mapping                       Pure math --- no dependencies

       1          Perceptual Core              OkLCH editing, ΔE calculation, contrast ratios (WCAG)            Oklab transform math; WCAG luminance formula

       2         Palette Structure                  Swatch + Role + Proportion + Adjacency model                        JSON schema / typed objects

       3         Constraint Engine                WCAG enforcement, CVD simulation, gamut clamping                       Rule-based; deterministic

       4        Feature Extraction     Extract semantic features: L/C/h stats, contrast stats, harmony scores              Analytical; rule-based

       5        Semantic Inference         Predict PAD vector + adjective embedding from palette features       Regression baseline + optional learned model

       6         Semantic Tracking       Semantic similarity, distance, invariant checks across transforms             Vector math; cosine similarity

       7       Generator / Optimizer       Palette search/generation given target semantics + constraints       Evolutionary or gradient-based optimization

       8                API                User-facing operations: generate, evaluate, transform, explain       REST/GraphQL; structured JSON schema output
  ----------- ----------------------- ------------------------------------------------------------------------ ----------------------------------------------

**8.2 The Palette Data Structure**

The fundamental data object that all engine operations act on:

  ------------------------ ----------------- ------------------------------------------------- ------------------------------------------------------------------------------------------------
         **Field**             **Type**                       **Description**                                                            **Example**

             id                 string                   Unique palette identifier                                                   \'brand-primary-v3\'

        swatches\[\]        array of Swatch              The color values in OkLCH                                      \[{l:0.55, c:0.18, h:240, role:\'primary\'}\]

        swatch.role              enum                  Semantic role in the palette             background \| surface \| text \| primary \| secondary \| accent \| error \| warning \| success

       swatch.weight         float \[0,1\]          Expected proportion of visual area                                     0.6 for background, 0.05 for CTA accent

       adjacency\[\]        array of pairs       Which swatches appear adjacent in layout                        \[\[\'background\',\'text\'\], \[\'surface\',\'primary\'\]\]

          topology               enum                      Harmony topology type                      monochromatic \| analogous \| complementary \| split-comp \| triadic \| functional

        semantic.vad          float\[3\]            Predicted Valence-Arousal-Dominance                                              \[0.65, 0.32, 0.41\]

    semantic.adjectives       string\[\]               Predicted semantic adjectives                                   \[\'trustworthy\', \'calm\', \'professional\'\]

   semantic.harmony_score    float \[0,1\]              Predicted aesthetic harmony                                                          0.78

        meta.locale             string        Cultural/locale context for semantic prediction                                \'en-US\' \| \'ja-JP\' \| \'pt-BR\'

        meta.domain             string                    Industry/context domain                                  \'healthcare\' \| \'fintech\' \| \'gaming\' \| \'food\'
  ------------------------ ----------------- ------------------------------------------------- ------------------------------------------------------------------------------------------------

**8.3 Semantic Feature Extraction**

Before running inference, extract interpretable features from any palette. These features serve as both model inputs and human-readable explanations:

  ------------------- ------------------------------------------------------- ------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------
   **Feature Group**                       **Features**                                                       **Computation**                                                                       **Semantic Interpretation**

   Lightness Profile           mean_L, min_L, max_L, L_range, L_std                                      Per-swatch OkLCH L values                                 Higher mean_L → more pleasant (PAD Pleasure). High L_range → high contrast, clear hierarchy.

    Chroma Profile          mean_C, max_C, C_range, colorfulness_energy              Per-swatch OkLCH C values; colorfulness_energy = mean_C × L_range                      Higher mean_C → more arousing, energetic. Low C → calm, neutral, corporate.

      Temperature                         warm_cool_ratio                      Proportion of swatches with h° in warm range (330°--90°) vs cool (150°--270°)         Warm dominant → energetic, appetite, action. Cool dominant → calm, trustworthy, clinical.

        Harmony          hue_dispersion, hue_cluster_count, topology_score                Std dev of hue angles; k-means on h° to count clusters               Low dispersion → monochromatic/analogous. High dispersion + small N clusters → complementary/triadic.

       Contrast        min_contrast, mean_contrast, role_contrast\[text→bg\]                   WCAG contrast formula on all adjacency pairs                                 Critical for accessibility layer; also predicts visual tension and energy.

     Semantic Load         unique_roles, role_balance, accent_prominence                 Entropy of role distribution; weight of non-neutral roles                      High accent prominence → bold, expressive. Balanced roles → harmonious, systematic.
  ------------------- ------------------------------------------------------- ------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------

**8.4 Semantic Operations API**

The high-level operations the engine exposes:

  ----------------------------------------- -------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------- -----------------------------------------------------------------------------
                **Operation**                                                              **Input**                                                                              **Output**                                                         **Underlying Mechanism**

              evaluate(palette)                                                          Palette object                                                 { vad, adjectives, harmony_score, contrast_report, cvd_report }            Feature extraction → semantic inference → constraint checking

   generate(target_semantics, constraints)                 { adjectives, vad_target, topology, domain, locale } + constraints object                       N candidate palettes ranked by semantic + harmony scores              Evolutionary optimization in OkLCH space; constraint enforcement

        transform(palette, operation)        Palette + operation spec { type: \'dark_mode\' \| \'accessible\' \| \'seasonal_warm\', strength: 0.8 }                 New palette with minimal semantic drift                 Semantic invariant optimization; fix h°, adjust L/C to meet new constraints

      similarity(palette_a, palette_b)                                                Two palette objects                                             { cosine_semantic: 0.87, vad_distance: 0.12, feature_diff: {\...} }        Cosine similarity on semantic embeddings + VAD Euclidean distance

         explain(palette, swatch_id)                                            Palette + optional focus swatch                                          Natural language explanation + feature contribution breakdown            Sensitivity analysis on semantic features; narrative generation

   suggest_variants(palette, variant_type)                                        Palette + variant type enum                                                3--5 variant palettes preserving semantic invariants              Sampling around palette in semantic space with constraint enforcement
  ----------------------------------------- -------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------- -----------------------------------------------------------------------------

**8.5 MVP Roadmap**

  -------------------------------- ----------------------------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------- ------------------------ ---------------------------
             **Phase**                                                                       **Scope**                                                                                              **Deliverable**                                      **Engineering Effort**       **ML Required?**

   Phase 1: Perceptual Foundation    HEX↔OkLCH conversion; WCAG contrast checker; ΔE distance; basic topology generator (mono/analogous/complementary/triadic)    Working color math library; palette generator for 6 topologies; accessibility report         1--2 weeks                    No

   Phase 2: Rule-Based Semantics    Feature extractor; PAD regression using literature priors; VAD→adjective mapping; basic semantic evaluate() and transform()     evaluate() returning VAD + adjective labels; dark_mode and accessible transforms           1--2 weeks           No (regression only)

     Phase 3: Learned Semantics         Train set encoder on Kuler/COLOURlovers data; multi-task model: harmony + adjectives + VAD; semantic similarity API             Full semantic inference; similarity() and suggest_variants() operations                3--6 weeks         Yes --- set encoder model

   Phase 4: Context Conditioning        Add locale, domain, modality as conditioning inputs; cultural calibration dataset; domain-specific convention rules                    Conditional semantic predictions; context-aware generation                      3--4 weeks         Yes --- conditional model

     Phase 5: Explanation Layer                     Sensitivity analysis per swatch/feature; narrative generation; semantic drift visualization                                     explain() operation; semantic tracking dashboard                           2--3 weeks              Optional (NLG)
  -------------------------------- ----------------------------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------- ------------------------ ---------------------------

**CHAPTER 9: ANTI-PATTERNS --- HOW COLOR SYSTEMS FAIL**

Understanding failure modes is as important as understanding best practices. This chapter documents the most common ways color systems --- and color psychology claims --- go wrong.

**9.1 Technical Anti-Patterns**

  ----------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------
                    **Anti-Pattern**                                                                                        **What Goes Wrong**                                                                                                                        **Correct Approach**

               Operating in sRGB hex space               Gradient midpoints look muddy; \'equal step\' lightness operations produce unequal perceptual steps; semantic features computed on non-perceptual numbers                    Convert to OkLCH for all internal computation; output to hex only for final rendering

       Treating palettes as unordered color lists                       Role effects are ignored; the same swatches in different roles produce completely different meanings and aesthetic outcomes                          Always model: swatch + role + proportion + adjacency. Compute semantics on the role-annotated structure.

      Using harmony type as a guarantee of quality                    A triadic palette can look terrible at equal proportion and saturation; a complementary pair can work at many saturation levels                Harmony topology is a starting constraint, not a quality guarantee. Validate with computed harmony score + human review.

   Ignoring the Mach band / banding issue in gradients                               Perceptually smooth gradients appear banded or striped on-screen due to lightness transition rate                                         Plot lightness in OkLCH as a function of gradient position; ensure monotonic and smooth transitions

        Building universal color→emotion mappings                                              Engine predicts wrong emotions for different locales, age groups, and domains                                                             Build meaning(palette \| locale, domain) --- never a universal meaning(palette)

          Testing palettes on a single display                              Colors look different across monitors, operating systems, and color profiles --- sRGB vs P3 vs uncalibrated screens                                         Test on calibrated sRGB + a wide-gamut display; test with WCAG tools; simulate CVD
  ----------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------

**9.2 Conceptual Anti-Patterns**

  --------------------------------------------------------------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                        **Claim / Anti-Pattern**                                                                                                                          **The Problem**                                                                                                                                                                                   **What the Evidence Actually Supports**

                  \'Red makes people hungry\' (general)                  This is an oversimplification used in fast-food branding that became self-fulfilling. The actual evidence for red specifically increasing appetite is weak; warmth and high saturation together may have effects.   High-saturation, high-contrast color combinations may increase arousal, which can interact with hunger --- but the hue-specific claim is not robustly supported independent of saturation and context.

                    \'Blue builds trust\' (universal)                        Widely repeated in design and marketing. Blue is associated with trust in specific contexts (tech, financial, medical) --- but this is a category/learned association, not a universal effect of the hue.                       Blue is a common color in categories perceived as trustworthy --- likely due to brand accumulation in those categories. The effect is domain-specific, not universal.

          \'Warm colors advance, cool colors recede\' (always)                           This is a rule of thumb in painting based on atmospheric perspective (blue haze = distance). It fails at high contrast differences and when luminance relationships are reversed.                                             Luminance (lightness) is a stronger depth cue than color temperature in most contexts. A bright cool color will \'advance\' over a dark warm one.

                      \'More color = more emotion\'                                   Some designers believe maximal saturation is always more impactful. High chroma raises arousal but can reduce preference and perceived quality, especially in premium/luxury contexts.                        Luxury and premium brand design typically uses restrained chroma. High chroma is appropriate for energy/youth/action contexts; low chroma signals quality, maturity, and sophistication.

   Citing \'studies show X% of purchase decisions are based on color\'                                  These statistics (often 60-90% figures) circulate widely but have no traceable, reliable primary source. They are not from peer-reviewed research.                                                 Color is an important cue in consumer decisions, but the specific percentages are fabricated or methodologically irreproducible. Use the actual PAD/EVT research instead.
  --------------------------------------------------------------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**PART II**

**COLOR GEOMETRY IN OKLCH**

*Treating Palettes as 3D Geometric Objects*

Point Clouds · Shape Classification · Hue-Plane Topology · Contrast Graphs · Geometric Operations

**CHAPTER 10: THE GEOMETRIC MODEL --- PALETTES AS 3D OBJECTS**

The foundational insight of Part II: a palette is not a list of hex values. When represented in OkLCH-Cartesian space, a palette becomes a **weighted point cloud in three-dimensional Euclidean space**. This reframing unlocks a family of geometric operations that give palette intelligence a rigorous mathematical foundation: centroid, covariance, hull volume, graph distance, and trajectory curvature.

+:--+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **PART II THESIS**                                                                                                                                                                                                                                                                                                          |
|   |                                                                                                                                                                                                                                                                                                                             |
|   | Everything computable about palettes --- balance, hierarchy, harmony, complexity, semantic drift, coherence --- can be derived from the geometry of a 3D point cloud. The semantic engine from Part I maps meaning onto this geometric substrate. Geometry is the computation layer; semantics is the interpretation layer. |
+---+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**10.1 Why Raw OKLCH Coordinates Are Insufficient for Geometry**

In OkLCH, hue is an angle (0--360 degrees) that wraps around. This creates a problem for Euclidean geometry: two colors at h=5 and h=355 are perceptually adjacent (both near red) but arithmetically distant. Any centroid or covariance computed directly in (L, C, h) space will be wrong near the wraparound. The solution is to convert the cylindrical hue-chroma plane to Cartesian coordinates:

  -------------------------- -------------------------------------- ------------------------------------------ -------------------------------------------------------------------
       **OkLCH Input**                 **Transformation**                      **Cartesian Output**                                   **Geometric Meaning**

   h (hue angle in degrees)          theta = h \* pi / 180              cos(theta), sin(theta) components       Converts circular angle to unit-circle position --- no wraparound

          C (chroma)          x = C\*cos(theta), y = C\*sin(theta)   x = green-red axis, y = blue-yellow axis            Chroma encodes distance from achromatic center

        L (lightness)                  z = L (no change)                          z = L directly                               Lightness maps to the vertical axis
  -------------------------- -------------------------------------- ------------------------------------------ -------------------------------------------------------------------

The resulting point for each swatch is: p_i = (x_i, y_i, z_i) in true 3D Euclidean space. Euclidean distance in this (x,y,z) space closely approximates OkLCH perceptual distance --- geometry here directly corresponds to perceived relationships.

**10.2 The Weighted Point Cloud**

Colors in a real palette do not carry equal visual weight. A background color covers 60-70% of visual area; an accent CTA may cover 2%. Geometric computations ignoring weights will give misleading results.

  -------------------------- ------------------------------------------------------------------------------------- ----------------------------------------------- ---------------------------------------------
      **Weight Source**                                        **How to Assign**                                                    **Use Case**                              **Default If Unknown**

      Role-based weights       Fixed prior: background=0.60, surface=0.20, text=0.10, accent=0.06, special=0.04     UI palette analysis; design system evaluation   Use role-based defaults from token taxonomy

    Image-derived weights     Run k-means on image pixels, map cluster centers to palette, weight by cluster size      Image recoloring; photo-dominant design          Not applicable without source image

        User-specified                    Designer provides proportional weights as palette metadata                      Precise brand palette description                  Equal weights as fallback

   Equal weights (fallback)                               w_i = 1/N for all swatches                                Exploratory analysis; no role data available          USE ONLY when no better option
  -------------------------- ------------------------------------------------------------------------------------- ----------------------------------------------- ---------------------------------------------

+:--+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **ENGINE RULE #2**                                                                                                                                                                                                                                      |
|   |                                                                                                                                                                                                                                                         |
|   | Every geometric computation on a palette should use weighted versions of the formulas. The weighted centroid, weighted covariance, and weighted hue balance give results that reflect actual visual dominance --- not a simple average across swatches. |
+---+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**CHAPTER 11: SHAPE ANALYSIS --- COMPUTING THE GEOMETRY DESCRIPTOR**

This chapter defines every component of the Geometry Descriptor: where the palette lives in 3D space, how large it is, what shape it forms, and how it is oriented. Each feature is directly computable, interpretable, and semantically meaningful.

**11.1 Position Features: Where the Palette Lives**

  -------------------------- ---------------------------------------------------------------------- --------------------------------------------------------------------------- --------------------------------------------------------------------------------
         **Feature**                                      **Formula**                                                       **Semantic Interpretation**                                                        **Typical Ranges**

    Weighted Centroid (mu)              mu = Sum(w_i \* p_i) / Sum(w_i) --- a 3D vector                The palette center of mass --- average visual presence in color space     mu_z: 0=very dark, 1=very light; sqrt(mu_x\^2+mu_y\^2) = mean chroma intensity

    Dominant Hue Direction    angle(mu_x, mu_y) --- hue angle of centroid projected onto hue plane       The warm/cool bias of the entire palette as a single hue reading             0-360 deg; near 0=red bias; near 240=blue bias; near 120=green bias

   Overall Chroma Intensity             sqrt(mu_x\^2 + mu_y\^2) = chroma of the centroid                    How colorful the palette is overall, accounting for weights                   0=achromatic; 0.15=muted; 0.25+=vivid; 0.35+=very saturated

            Medoid                      Swatch i\* = argmin Sum_j(w_j \* dist(p_i, p_j))             Most representative swatch --- best single stand-in for the whole palette                   Use for palette thumbnail / avatar color in UI
  -------------------------- ---------------------------------------------------------------------- --------------------------------------------------------------------------- --------------------------------------------------------------------------------

**11.2 Spread Features: How Big Is the Palette?**

  ------------------------- ------------------------------------------------------ ------------------------------------------------------- -------------------------------------------------------------------------------------------------------
         **Feature**                             **Formula**                                     **Semantic Interpretation**                                                       **Design Implication**

   Lightness Span (DeltaL)                   max(z_i) - min(z_i)                     How much of the lightness axis the palette occupies    DeltaL \> 0.6: strong hierarchy potential. DeltaL \< 0.2: flat, same-level --- risk of poor contrast.

     Chroma Radius Stats     r_i = sqrt(x_i\^2 + y_i\^2); report min/mean/max/std   Vividity of each swatch; spread of saturation levels      High std(r): mixes vivid accents with neutral grounds. Low std(r): uniform saturation throughout.

     Convex Hull Volume              Volume of 3D convex hull of all p_i                True territory of the palette in color space                   Small hull: coherent, tight, focused. Large hull: expressive, varied, complex.

    Hull SA/Volume Ratio                Surface area divided by volume              Relative flatness vs compactness of the palette shape                High ratio: thin sheet-like palette. Low ratio: compact, spherical palette.
  ------------------------- ------------------------------------------------------ ------------------------------------------------------- -------------------------------------------------------------------------------------------------------

**11.3 Shape Type via PCA Eigenvalues**

The most powerful structural descriptor: Principal Component Analysis on the weighted point cloud. Compute the weighted covariance matrix: Sigma = Sum_i(w_i \* (p_i - mu)(p_i - mu)\^T) / Sum(w_i). Extract eigenvalues lambda_1 \>= lambda_2 \>= lambda_3.

  --------------------------------------------- -------------------------------------- ----------------------------------------------------------- ----------------------------------------------------------- -------------------------------------------------------------------------------------
             **Eigenvalue Pattern**                      **Geometric Shape**                              **Palette Archetype**                                      **Semantic Signature**                                                   **Best Design Context**

   lambda_1 \>\> lambda_2 \~ lambda_3 (needle)   Points arranged along a single axis        Monochromatic ramp, tonal scale, lightness ladder            Minimal, disciplined, strong hierarchy, precise              UI text/surface ladders, data viz sequential, typography-forward brand

   lambda_1 \~ lambda_2 \>\> lambda_3 (sheet)          Points lie in a 2D plane         Same-lightness multi-hue brand palette, editorial palette   Varied but coherent; same visual weight level across hues   Brand systems with multiple hue families at matched lightness; infographic palettes

    lambda_1 \~ lambda_2 \~ lambda_3 (cloud)     Points distributed in all directions      Rich editorial palette, comprehensive design system        Maximum variety; powerful but easiest to make chaotic      Large design systems, generative art, illustration with strong proportion control
  --------------------------------------------- -------------------------------------- ----------------------------------------------------------- ----------------------------------------------------------- -------------------------------------------------------------------------------------

Derived scalar shape scores:

  ------------ ---------------------------------- ----------- -----------------------------------------------------------------------
   **Score**              **Formula**              **Range**                                **Meaning**

   Linearity        1 - lambda_2 / lambda_1        \[0, 1\]        Near 1: needle-like, single-axis palette. Near 0: not linear.

   Planarity        1 - lambda_3 / lambda_2        \[0, 1\]          Near 1: sheet-like, two-axis palette. Near 0: not planar.

   Sphericity         lambda_3 / lambda_1          \[0, 1\]    Near 1: volumetric cloud palette. Near 0: collapsed to line or plane.

   Anisotropy   (lambda_1 - lambda_3) / lambda_1   \[0, 1\]             Overall shape complexity; complement of sphericity.
  ------------ ---------------------------------- ----------- -----------------------------------------------------------------------

**11.4 Orientation and Lightness-Chroma Coupling**

The first principal component (v_1) gives the direction of maximum variance. If v_1 points mostly along z: palette varies mainly in lightness (hierarchy-focused). If v_1 points mostly in (x,y): palette varies mainly in hue/chroma (expressive, brand-driven).

Lightness-Chroma Coupling --- one of the most diagnostically rich single numbers in the geometry descriptor:

  ----------------------- ---------------------------------------------------------- ---------------------------------------------------------------------- ---------------------------------------------------------------
     **Coupling Type**                           **Formula**                                                **Semantic Association**                                             **Example Palettes**

   Positive L-C coupling   corr(z_i, r_i) \> 0 (brighter colors are more saturated)        Fresh, candy, pop, neon-bright; airy and vibrant together           Pastel systems, candy UI, spring/summer seasonal palettes

   Negative L-C coupling    corr(z_i, r_i) \< 0 (darker colors are more saturated)         Moody, cinematic, neon-on-black, deep luxury; jewel tones            Dark mode neon, luxury fashion, cinematic color grading

    Near-zero coupling      \|corr\| \< 0.2 (saturation independent of lightness)     Balanced systems; saturation is a free variable; engineered palettes   Brand systems with separate lightness and saturation controls
  ----------------------- ---------------------------------------------------------- ---------------------------------------------------------------------- ---------------------------------------------------------------

**CHAPTER 12: HUE-PLANE TOPOLOGY & CONTRAST GRAPH ANALYSIS**

Two specialized geometric analyses that encode palette structure in ways eigenvalues alone cannot capture: the topology of how hues distribute around the color wheel, and the graph structure of contrast relationships between swatches.

**12.1 Hue Balance: The Resultant Vector**

Project all swatches onto the hue-chroma plane and compute the weighted resultant vector:

R = \| Sum_i(w_i \* (x_i, y_i)) / Sum(w_i) \|

  ------------------------------- ---------------------------------------------------- -------------------------------------------------------- -------------------------------------------------------------------
            **R Value**                            **Interpretation**                                    **Semantic Profile**                                               **Example**

         R \~ 0 (balanced)         Hues cancel out --- chromatic neutral in aggregate    Harmonious, neutralized; no dominant color statement    Triadic system at equal weights; warm+cool balanced brand palette

   R = 0.05-0.30 (moderate lean)   Directional hue bias with some internal diversity     Recognizable color identity with supporting contrast      Most brand palettes: primary dominant with secondary accents

      R \> 0.50 (strong lean)          Strongly dominated by a single hue family        Clear single-mood identity; monochromatic or analogous          Pure monochromatic, strong single-hue brand systems
  ------------------------------- ---------------------------------------------------- -------------------------------------------------------- -------------------------------------------------------------------

**12.2 Arc Length Coverage and Complementarity Index**

Weighted Hue Arc: find the minimum circular arc enclosing swatches containing 80% or more of total weight.

  ---------------------- -------------------------------------- ------------------------------------------------------ ------------------------------------------------------
   **Weighted Hue Arc**            **Topology Label**                            **Semantic Profile**                                     **Primary Risk**

        \< 40 deg           Monochromatic / tight analogous       Coherent, focused, minimal; single emotional note     Monotony without sufficient L contrast between roles

        40-90 deg                      Analogous                   Natural, organic, calm; allows some hue contrast          Roles may blend without L contrast support

        90-180 deg        Wide analogous / split complementary        Expressive variety with residual coherence        Needs proportion control to avoid visual competition

       180-270 deg            Complementary / near-triadic       High tension, drama, energy; strongest visual impact      Visual vibration if both poles are high-chroma

        \> 270 deg         Triadic / tetradic / full spectrum               Maximum variety; rich, complex                   Chaotic without strict dominance hierarchy
  ---------------------- -------------------------------------- ------------------------------------------------------ ------------------------------------------------------

Continuous Complementarity Index: measure weighted mass in the opposing 180-degree sector (plus or minus 30 degrees tolerance). Normalize to \[0, 0.5\]. Near 0 = monochromatic. Near 0.5 = equal-weight complementary.

+:--+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **DESIGN INSIGHT**                                                                                                                                                                                                                                                                                 |
|   |                                                                                                                                                                                                                                                                                                    |
|   | The most commercially successful palettes typically have a complementarity index between 0.15 and 0.35 --- a strong dominant hue (roughly 80% visual weight) with a carefully sized opposing accent (roughly 20%). A pure 0.5 complementary is often too visually aggressive for sustained UI use. |
+---+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**12.3 The Contrast Graph**

Build an undirected weighted graph: nodes are swatches, edge weights are Euclidean distances in (x,y,z) OkLCH-Cartesian space (closely approximating perceptual delta-E).

  ----------------------- --------------------------------------------------------- ----------------------------------------------------------------------- ----------------------------------------------------------
     **Graph Metric**                          **Computation**                                               **Semantic Meaning**                                           **Target for UI Systems**

   Minimum edge distance                min of all pairwise distances                Risk of swatches collapsing --- two colors too similar to distinguish      \> 0.12 Oklab units between any adjacent role pair

   Maximum edge distance                max of all pairwise distances                Drama and tension potential; highest-contrast relationship in palette      Background-to-text edge should be near the maximum

     MST total length            Total edge weight of minimum spanning tree                  Minimum perceptual bandwidth to connect all swatches            Higher MST = more diverse palette; lower = more coherent

      Graph diameter             Longest shortest-path between any two nodes               Full perceptual range from most-different pair in palette                   Should span most of available DeltaL

      Clusterability       Ratio of inter-cluster to intra-cluster distances (k=2)        Whether palette splits naturally into neutrals and accents                 High clusterability = good UI structure
  ----------------------- --------------------------------------------------------- ----------------------------------------------------------------------- ----------------------------------------------------------

**12.4 Detecting Neutral Backbone + Accent Structure**

Detection algorithm:

1.  Apply k=2 clustering on the (x, y, z) point cloud with weights

2.  Classify cluster with lower mean radius (r) as \'neutrals\'; higher mean r as \'accents\'

3.  Compute separation index: inter-cluster distance / intra-cluster distance

4.  If separation \> 1.5, neutral-backbone structure is confirmed

  ---------------------------------- ------------------------------------------------ ---------------------------------------------------------------- -------------------------------------------------------
          **Structure Type**                       **Cluster Pattern**                                     **Semantic Signature**                                           **Best For**

   Neutral backbone + accent spikes     Tight low-r cluster + 1-2 high-r outliers                Professional, functional, hierarchy-clear                  SaaS UI, enterprise apps, productivity tools

          Dual-pole palette            Two clusters at high r, opposing hue angles       High tension, dynamic; complementary with strong identity          Sports, gaming, energy brands, campaign pages

            Gradient spine            Points along a diagonal --- L increases with r        Tonal, luminous; colors breathe through the palette         Lifestyle brands, editorial, photography-heavy design

            Uniform cloud             No clear clustering; similar r, varied h and L   Comprehensive identity requiring careful proportion management          Design systems for large organizations
  ---------------------------------- ------------------------------------------------ ---------------------------------------------------------------- -------------------------------------------------------

**CHAPTER 13: GRADIENTS AS GEOMETRIC TRAJECTORIES**

Chapter 5 covered the physics and interpolation science of gradients. The geometric model reframes gradients as paths through 3D OkLCH-Cartesian space --- a perspective that enables precise quality metrics and semantic control that interpolation-space decisions alone cannot provide.

**13.1 The Trajectory Model**

A gradient is a parametric curve in 3D OkLCH-Cartesian space: gamma(t) in R\^3, t in \[0, 1\]. For a linear two-stop gradient, gamma(t) is a straight line segment. For multi-stop gradients, it is a piecewise-linear or smooth curve.

  ------------------------ ----------------------------------------------------------- --------------------------------------------------- ------------------------------------------------------------------------------------------------
   **Trajectory Feature**                        **Definition**                                       **Semantic Meaning**                                                      **Quality Threshold**

        Path length                Integral of \|gamma\'(t)\| dt over \[0,1\]              Total perceptual change across the gradient                       Longer = more expressive/dynamic. Shorter = subtle/refined.

   Lightness monotonicity      Is z(t) = L monotonically increasing or decreasing?          Smooth directional luminance progression            Must be monotonic for sequential data viz; strongly preferred for calm/depth gradients

         Curvature            Average \|gamma\'\'(t)\| --- how much the path bends      Hue or chroma changes during gradient; twistiness               Low curvature = calm, atmospheric. High curvature = electric, dynamic.

    Chroma arc direction    Does chroma increase, decrease, or peak at mid-gradient?         Saturation narrative along the gradient        Calm: C decreases toward end. Atmospheric: C peaks at mid. Electric: C constant at high value.

    Uniform step spacing    Sample at equal t; check if Euclidean distances are equal   Perceptual smoothness --- are visual steps equal?          Coefficient of variation of step sizes \< 0.1 for smooth; \> 0.3 = banding risk
  ------------------------ ----------------------------------------------------------- --------------------------------------------------- ------------------------------------------------------------------------------------------------

**13.2 Gradient Archetype Library**

  ------------------- ---------------------------------------------------------------------------------- -------------------------------------------------------- ------------------------------------------------------------------
     **Archetype**                                **Trajectory Description**                                             **Semantic Association**                                        **Typical Use Case**

    Luminance shaft                   Straight line mostly along z-axis; low xy movement                      Depth, shadow, premium dark, subtle atmosphere        Background gradients, card depth, dark-mode surface hierarchy

   Temperature sweep       Line moving through hue plane from warm to cool; constant or monotonic L       Transition, sunset/dusk, emotional shift, time passage           Hero sections, state transitions, temporal data

     Chroma bloom             Path spirals outward in r as it moves along z; L increases with C               Luminous, fresh, alive, colors coming to life              Brand gradients, product reveals, lifestyle branding

     Electric arc            High curvature in hue plane; large C throughout; multiple hue stops              Energy, technology, digital-native, synthwave           Tech brand gradients, game UI, generative art backgrounds

     Mist dissolve               C decreases toward endpoint; L increases; minimal hue drift                       Fading, memory, softness, dream-like             Fade overlays, soft editorial gradients, photography backdrops

   Diverging bridge    Starts at high-L neutral center, curves outward in two directions simultaneously          Balance, comparison, deviation, judgment          Data viz diverging scales, before/after comparisons, risk gauges
  ------------------- ---------------------------------------------------------------------------------- -------------------------------------------------------- ------------------------------------------------------------------

**CHAPTER 14: GEOMETRY-DRIVEN PALETTE OPERATIONS**

The full power of the geometric model is realized in palette operations: transforms that act on the 3D point cloud with predictable, controllable outcomes. This chapter defines the complete operator vocabulary.

**14.1 Global Transforms (Acts on Entire Shape)**

  ------------------------------- -------------------------------------------------------- ---------------------------------------------------------------------- --------------------------------------------------------------------- --------------------------------------------------------
           **Operator**                             **Geometric Action**                                              **OkLCH Effect**                                                     **Semantic Effect**                                               **Constraint**

   Translate z (lightness shift)                  Shift all z_i by Delta_z                                  Lighten or darken palette uniformly                    Dark shift: more dominant/serious. Light shift: more pleasant/airy.    Clamp all z_i to \[0.05, 0.98\]; recheck WCAG after

    Scale radius (chroma shift)        r_i -\> alpha \* r_i (scale x_i, y_i by alpha)           Saturate (alpha\>1) or desaturate (alpha\<1) proportionally          Scales VAD Arousal: desaturate=calmer; saturate=more energetic      Clamp to gamut; alpha\>1 requires gamut boundary check

   Rotate z-axis (hue rotation)      Rotate all (x_i, y_i) by angle theta around z-axis     Shift all hues by theta degrees; preserve relative hue relationships    Changes contextual associations while preserving internal harmony     No gamut issue from rotation alone; check at high C

     Non-uniform scale by role     Apply different alpha per cluster (e.g., accents only)           Boost accent chroma without changing neutral chroma              Increases punch without changing structural harmony of neutrals      Recheck minimum distance on accent-to-neutral edges
  ------------------------------- -------------------------------------------------------- ---------------------------------------------------------------------- --------------------------------------------------------------------- --------------------------------------------------------

**14.2 Shape Editing (Structural Change)**

  ------------------------- -------------------------------------------------- ------------------------------------------------------------------------------------------ ----------------------------------------------------------------
     **Desired Outcome**                   **Geometric Target**                                                      **Operation**                                                            **Example Application**

   More coherent / tighter    Reduce hull volume; decrease eigenvalue spread         Move swatches toward centroid: p_i -\> mu + alpha\*(p_i - mu) with alpha \< 1             Calm down a chaotic editorial palette for product use

        Add hierarchy        Increase DeltaL; create ordered lightness ladder   Sort by role; assign L values from monotonic ramp (0.08 dark text to 0.95 light surface)         Generate UI tonal system from a flat brand palette

     Add energy / punch      Increase max radius; increase max edge distance      Selectively increase C for accent swatches; verify min distance to neutrals is safe              Electrify a muted palette for campaign variant

      Warm the palette           Rotate centroid hue toward \~30 degrees                   Rotate (x_i, y_i) by target angle for all or accent swatches only               Create seasonal warm autumn variant from neutral brand palette

    Prepare for dark mode     Translate z downward; invert role assignments        Swap background (high L) and text (low L) roles; maintain hue and chroma structure          Generate dark-mode variant with minimal semantic drift
  ------------------------- -------------------------------------------------- ------------------------------------------------------------------------------------------ ----------------------------------------------------------------

**14.3 Semantic-to-Geometric Mapping (Data to Color Compiler)**

The ultimate application: mapping meaningful data dimensions directly to geometric controls, making the palette engine a data-to-geometry-to-color compiler.

  ------------------------------- ---------------------------------------------- ----------------------------------------------------------------------------------------------- -------------------------------------------------------------
   **Data / Semantic Dimension**              **Geometric Control**                                                     **OkLCH Effect**                                                            **Example Application**

      Intensity / Importance           Chroma radius r of relevant swatches                          Higher importance = higher C; lower = toward achromatic                      Risk dashboard: high-risk items vivid; low-risk items muted

          Hierarchy level            Lightness z (descending with importance)             Most important: highest L contrast with background; least: near background L              5-level type scale generated from a single brand color

    Emotional warmth / coolness       Hue angle theta (rotation of centroid)                          Warmer = shift toward 30 deg; cooler = toward 220 deg                       Adaptive UI: social content warm vs analytical content cool

      Confidence / Certainty       Chroma C (higher certainty = more saturated)                  Uncertain states: muted/gray. High certainty: full brand color.                        Data viz: confidence intervals shown as C ramp

     Calmness / Arousal target       Chroma × contrast (both scale together)                   Calm: low C + low contrast edges. Aroused: high C + high contrast.                        Contextual theming: focus mode vs alert mode

   Positive / Negative sentiment           Hue rotation + L adjustment            Positive: shift toward system positive hue + raise L. Negative: toward warning hue + lower L.       Sentiment-aware color coding in monitoring systems
  ------------------------------- ---------------------------------------------- ----------------------------------------------------------------------------------------------- -------------------------------------------------------------

**14.4 The Complete Geometry Descriptor Object**

  --------------------------------------------------- ------------------ ----------------------------------- -------------------------------------------------------
                 **Descriptor Field**                      **Type**               **Computed From**                             **Semantic Use**

                 centroid \[x, y, z\]                     float\[3\]      Weighted mean of (x_i, y_i, z_i)    Dominant hue direction + overall L + chroma intensity

     eigenvalues \[lambda_1, lambda_2, lambda_3\]         float\[3\]      PCA on weighted covariance matrix            Shape type: needle / sheet / cloud

   shape_scores { linearity, planarity, sphericity }      float\[3\]       Derived from eigenvalue ratios       Shape classification + semantic archetype lookup

                   principal_axis v1                      float\[3\]       First eigenvector of covariance         Primary axis: L-dominated vs hue-dominated

                      lc_coupling                      float \[-1, 1\]             corr(z_i, r_i)                  Fresh/pop vs moody/cinematic coupling style

                    lightness_span                      float \[0, 1\]           max(z_i) - min(z_i)                           Hierarchy potential

         chroma_stats { min, mean, max, std }             float\[4\]               From r_i values                    Energy level, accent-neutral balance

                     hue_balance R                      float \[0, 1\]       Resultant vector magnitude                   Dominant hue focus vs balance

                      hue_arc_deg                      float \[0, 360\]     Weighted minimum covering arc         Topology: monochromatic through full-spectrum

                 complementarity_index                 float \[0, 0.5\]     Weighted opposite-sector mass                  Complementary tension level

                      hull_volume                           float           3D convex hull of point cloud             Primary diversity / complexity metric

                    graph_min_dist                          float           Minimum pairwise edge weight               Collapse risk --- must exceed 0.12

                   graph_mst_length                         float                 MST total weight                      Connectivity / contrast bandwidth

                    clusterability                     float \[0, inf\]     k=2 cluster separation ratio               Neutral-backbone structure presence

         cluster_labels { neutrals, accents }               object             k-means on point cloud             Role prediction if formal roles not provided
  --------------------------------------------------- ------------------ ----------------------------------- -------------------------------------------------------

**14.5 Gamut Boundary Awareness**

+:--+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **CRITICAL CONSTRAINT: THE OkLCH SPACE IS NOT A PERFECT CYLINDER**                                                                                                                                                                                                                                                  |
|   |                                                                                                                                                                                                                                                                                                                     |
|   | The available OkLCH colors displayable in sRGB form an irregular, non-symmetric solid --- not a perfect cylinder. High-chroma yellows exist at very different max-C values than high-chroma blues. Any geometric operation that increases chroma or rotates hue MUST check gamut validity for each resulting color. |
+---+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Gamut management strategy:

5.  After every geometric operation, check each resulting swatch against the target gamut boundary

6.  If out of gamut: prefer chroma compression --- reduce C at constant L and h until in-gamut. This preserves hue identity and lightness hierarchy.

7.  Avoid clip-to-nearest-in-gamut --- it can shift hue, which breaks semantic identity

8.  For operations requiring maximum C, precompute C_max(L, h) for the target gamut and use it as ceiling in optimization

**14.6 Palette Shape Archetypes Reference**

  ------------------------ ----------------------------------- --------------------------------- ----------------------- ----------------------------------------- ------------------------------------------------------
     **Archetype Name**               **PCA Shape**                    **Hue Balance R**               **Hue Arc**                   **L-C Coupling**                                **Best Use Case**

           Needle               Needle (linearity \> 0.8)           Strong lean (R \> 0.4)              \< 30 deg              Strongly positive or negative               Tonal scales, monochromatic UI systems

            Fan                 Sheet (planarity \> 0.6)        Balanced to moderate (R \< 0.3)        60-120 deg                        Near zero                   Brand systems with hue variety at equal lightness

          Bipolar               Sheet (planarity \> 0.5)           Near-balanced (R \< 0.2)             \~180 deg                        Variable                    Complementary brand palettes, high-tension designs

   Neutral Spine + Spikes    Needle (spine) + outlier points         Moderate (R 0.2-0.5)         \< 60 deg for accents   Negative (neutrals dark, accents vivid)       UI design systems, SaaS products, enterprise

       Helix Gradient       Diagonal needle with L-C coupling             Strong lean                   \< 45 deg                     Strong positive               Smooth luminous gradients, lifestyle brand gradients

           Cloud               Sphere (sphericity \> 0.5)                Near-balanced                 \> 270 deg                        Variable                    Comprehensive design systems, illustration systems
  ------------------------ ----------------------------------- --------------------------------- ----------------------- ----------------------------------------- ------------------------------------------------------

**PART III**

**THE INTELLIGENCE PLATFORM**

*From Color Coordinates to a Full System of Interconnected Services*

Variables · Surface Map · Service Primitives · Assignment · Advanced Constructs · Capability Matrix

*Designed for visualization of thousands of nodes --- and beyond*

**CHAPTER 15: THE COMPLETE VARIABLE SPACE --- BEYOND L, C, AND h**

OkLCH gives you three coordinates. But building an intelligent color system for thousands of nodes requires commanding a far larger variable space. This chapter catalogs **every dimension at your disposal** --- from sub-pixel physics to temporal dynamics to user psychology --- organized by the space each variable inhabits.

+:--+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **PART III THESIS**                                                                                                                                                                                                                                                                                                                         |
|   |                                                                                                                                                                                                                                                                                                                                             |
|   | A palette engine built on OkLCH alone is a calculator. The platform described in Part III is a compiler --- it maps meaning, data, context, and constraints through successive transformation layers down to final pixel assignments. Each chapter in Part III defines one such transformation layer as an independent, composable service. |
+---+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**15.1 Color Coordinate Variables (Micro-Level)**

These are the intrinsic variables of a single color token:

  -------------------------- --------------------------------------------------------- ------------------------------------------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------
         **Variable**                               **Domain**                                                               **What It Controls**                                                                                      **Engine Relevance**

        L (Lightness)                                \[0, 1\]                                            Perceived luminance; primary driver of hierarchy and contrast                                  Strongest predictor of Pleasure and Dominance in PAD model; drives WCAG compliance

          C (Chroma)                               \[0, \~0.4\]                                                       Perceived colorfulness / vividness                                                       Primary driver of Arousal; encodes energy level and accent prominence

        h (Hue angle)                               \[0°, 360°)                                      Perceived hue identity; warm-cool axis; cultural association channel                            Weakest direct emotion driver but critical for category identity and learned associations

       alpha (opacity)                               \[0, 1\]                                                Transparency; how much the background bleeds through                               Compositing-aware: same OkLCH can read very differently at different alpha on different backgrounds

      Gamut feasibility                      Boolean per target space                                  Whether this color is physically realizable in sRGB / P3 / print                               Must be enforced after every geometric operation; chroma compression strategy required

   White point / illuminant                      D50, D65, custom                       The reference \'white\' the color is defined relative to --- changes all appearance predictions                 Affects any appearance service; critical for cross-media (screen-to-print) accuracy

          Blend mode          Enum: normal, multiply, screen, overlay, difference\...                           How a layer composites onto what is beneath it                              Same color in multiply mode reads dramatically different from normal; must be tracked in rendering service

     Tone mapping / gamma                        Curve parameters                                           How the display pipeline encodes and decodes luminance                        Gradient quality and perceived lightness uniformity depend on this; Oklab compensates for sRGB gamma internally
  -------------------------- --------------------------------------------------------- ------------------------------------------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------

**15.2 Spatial Variables (Pixels Are Not Isolated)**

No color exists in isolation. Every swatch is perceived in the context of its spatial neighborhood:

  ---------------------------------- --------------------------- -------------------------------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------
             **Variable**                    **Domain**                                           **What It Controls**                                                                                            **Engine Relevance**

           Area proportion               \[0, 1\] per swatch      How much of the visual field each color occupies --- determines perceptual dominance                           Must be encoded as palette weights; smallest area = least dominant regardless of chroma

           Adjacency graph               Graph over swatches       Which colors touch in the rendered output --- drives simultaneous contrast effects                   Needed in Constraint Service and Perception Service; colors that never touch have no contrast requirement

   Edge density / spatial frequency            Scalar               How \'busy\' a region is --- high frequency reduces legibility of embedded text                              Salience predictions must account for background complexity, not just background color

          Depth / z-ordering              Ordinal or float            Which elements are visually \'in front\'; affects how colors are composited                         Foreground elements need sufficient contrast from both their direct background and deeper backgrounds

     Local contrast neighborhood      Floating window of pixels      The effective \'background\' for any given pixel is not always a single swatch                                      Rendering service must account for mixed backgrounds on text and icons

       Spatial hierarchy level          Integer or tree depth        Position in the layout hierarchy (page \> section \> card \> element \> text)       Lightness ladders should map to spatial hierarchy: highest-level containers take neutral colors; deepest elements take maximum contrast
  ---------------------------------- --------------------------- -------------------------------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------

**15.3 Temporal Variables**

Color systems that exist over time have additional degrees of freedom:

  ------------------------------ ------------------------------------------------------------------------ --------------------------------------------------------------------------------------------------------- ------------------------------------------------------------------------------------------------------------------------------
           **Variable**                                         **Domain**                                                                          **What It Controls**                                                                                                 **Engine Relevance**

        Motion / animation                       Speed, easing, trajectory in color space                                             How a color transitions from one state to another                                Animated transitions are gradients in both space and time; trajectory curvature (Ch. 13) applies to time-transitions too

         Adaptation drift                                    Scalar over time                              Prolonged exposure to a dominant hue shifts the observer\'s perceived neutrality toward the complement    Important for dashboards / monitoring UIs that stay on-screen for hours; periodic subtle hue rotation can counteract fatigue

           State layers           Enum: normal / hover / selected / focused / disabled / error / loading   The same semantic token must have per-state color variants that preserve identity while signaling state    Assignment Service must expand each token to a full state matrix; disabled should desaturate (reduce C), not just change L

        Temporal stability                                    Penalty weight                                    For dynamic / streaming graphs: how much color assignment is allowed to change between frames            Assignment Service must support a stability constraint: minimize sum of color-change magnitudes across frame updates

   Recency / freshness encoding                            Continuous \[0, 1\]                                                     Color encodes how recently a node was active or updated                                   Map recency to chroma: fresh = high C; stale = desaturated; implement as a data-to-geometry mapping (Ch. 14)
  ------------------------------ ------------------------------------------------------------------------ --------------------------------------------------------------------------------------------------------- ------------------------------------------------------------------------------------------------------------------------------

**15.4 Data and Structure Variables (Graph-Specific)**

For large graph visualizations --- thousands of nodes and edges --- the data attributes themselves become color-driving variables:

  -------------------------------- --------------------------------------------- ---------------------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------
         **Data Variable**                           **Type**                                                        **Color Encoding Strategy**                                                                                  **Service Responsible**

      Node community / cluster                Categorical (N groups)              Assign distinct qualitative hue per community; match L and C across communities for equal salience                         Assignment Service + Constraint Service (CVD safety across N hues)

    Node importance / centrality                Continuous \[0, 1\]                                  Map to chroma C; high centrality = vivid; peripheral = muted                                                Assignment Service (data-to-geometry mapping from Ch. 14)

       Node value / magnitude                  Continuous or ordinal                                 Map to lightness L; create sequential colormap (monotonic L)                                                    Synthesis Service (sequential palette generation)

   Edge type / relationship class                   Categorical                         Edges need their own independent color vocabulary; must not conflict with node colors          Rendering Service + Assignment Service; edges often require transparency or desaturation to avoid visual noise

       Edge weight / strength                   Continuous \[0, 1\]                     Map to edge opacity (alpha) or thickness; color reserved for type, alpha for magnitude                                      Visual Channel Orchestrator (prevent color-overload)

   Node uncertainty / confidence                Continuous \[0, 1\]                               Map to chroma C: high confidence = vivid; uncertain = desaturated                                      Assignment Service; can be combined with value mapping using L-C coupling

      Node sentiment / valence                 Continuous \[-1, +1\]                      Map to hue shift: positive toward system positive hue; negative toward warning hue                                   Assignment Service with semantic-to-geometric mapping (Ch. 14)

            Node status             Enum: active / inactive / error / highlight     State layer expansion per node; error should use system warning hue; inactive should reduce C                                             Assignment Service state matrix
  -------------------------------- --------------------------------------------- ---------------------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------

**15.5 Meaning and Context Variables**

The most open-ended category --- variables that condition what any color means:

  ---------------------- ------------------------------------------------------------------------ --------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------
   **Context Variable**                                 **Values**                                                                                   **Effect on Meaning**                                                                                            **How to Encode**

          Domain             finance, healthcare, gaming, education, creative, industrial\...         Changes learned associations: blue means \'trustworthy\' in finance; \'cold\' in healthcare; \'magical\' in gaming               Locale + domain token passed to Semantic Embedding Service as conditioning input

    Audience / locale                               Culture + language                                                 Cross-cultural variation in hue-emotion mapping (see Ch. 3); color naming varies                        Cultural prior tables from Jonauskaite et al. 2020; locale parameter in all semantic predictions

      Brand anchors                            Fixed hue(s) / palette seeds                                                   Hard constraints: certain hues must appear and must not be changed                                    Constraint Service: anchor swatches are pinned; optimization only moves free variables

        Task mode               exploration / decision-making / monitoring / storytelling          Different tasks require different visual channels: monitoring needs salient alerts; storytelling needs coherent narrative              Visual Channel Orchestrator reads task mode to allocate encoding channels

      Emotion target      calm / urgent / playful / authoritative / trustworthy / innovative\...                              The intended PAD/VAD vector that the overall palette should land in                                            Input to Synthesis Service; drives the generation objective function

    Viewing condition            ambient luminance, display calibration, viewing distance                                  Changes apparent lightness, saturation, and simultaneous contrast effects                              Perception Service conditioning; must predict adjustments for dark vs bright environments
  ---------------------- ------------------------------------------------------------------------ --------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------

**CHAPTER 16: THE SERVICE ARCHITECTURE --- 13 INDEPENDENT MODULES**

The platform is not a monolith. It is a set of 13 independent services with clean input/output contracts that can be composed, replaced, or extended without breaking others. This chapter defines each service\'s purpose, interface, and the mathematical foundations it relies on.

+:--+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **DESIGN PHILOSOPHY**                                                                                                                                                                                                                                                                                                                                                                                                      |
|   |                                                                                                                                                                                                                                                                                                                                                                                                                            |
|   | Each service is visualization-agnostic. The Assignment Service does not know it is coloring a graph --- it receives entities with attributes and returns color tokens. The Rendering Service does not know what the semantic targets were --- it receives color assignments and scene parameters. This independence allows the same platform to serve graph visualization, UI theming, data dashboards, and brand systems. |
+---+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**16.1 Service Dependency Graph**

The 13 services form a layered dependency graph. The canonical service numbering (S1--S13) is consistent across all chapters. Lower-numbered services are lower-level and have fewer dependencies.

  --------------------------------- ------------- ----------------------------- -----------------------------------
             **Service**              **Layer**          **Depends On**                     **Used By**

          S1: Color Kernel           Foundation        Nothing (pure math)                 All services

       S2: Gamut & Color Mgmt        Foundation                S1                      S3, S5, S8, S12, S13

        S3: Palette Geometry          Analysis               S1, S2                         S7, S9, S13

     S4: Appearance & Perception      Analysis               S1, S2                        S5, S11, S13

       S5: Constraint & Safety       Validation            S1, S2, S4                      S9, S11, S13

       S6: Semantic Embedding         Inference              S1, S3                      S7, S9, S11, S14

     S7: Semantic Knowledge Base       Memory                  S6                             S6, S9

   S8: Visual Channel Orchestrator   Allocation                S6                         S11 (pre-step)

        S9: Palette Synthesis        Generation        S1, S3, S5, S6, S7                       S11

    S10: Spatial Context & Layout      Context                 S1                               S11

     S11: Assignment & Encoding      Application   S1, S4, S5, S6, S8, S9, S10                  S13

    S12: Rendering & Compositing       Output            S1, S2, S4, S11           Final pixels; feedback to S13

     S13: Telemetry & Benchmark       Learning           All (observer)             S6, S7, S9 (model updates)
  --------------------------------- ------------- ----------------------------- -----------------------------------

**16.2 S1: Color Kernel Service**

  -----------------------------------------------------------------------
                **S1 --- COLOR KERNEL \| Foundation Layer**

  -----------------------------------------------------------------------

The mathematical CPU of the platform. Every other service that touches color coordinates calls the Color Kernel. It must be correct, fast, and gamut-aware.

  ----------------------------- ----------------------------------- ----------------------------- ---------------------------------------------------------------------
          **Endpoint**                       **Input**                       **Output**                                    **Math Foundation**

     convert(color, toSpace)        ColorSpec + target space ID       ColorSpec in target space     Linear transforms via XYZ reference hub; gamma encoding/decoding

     distance(a, b, metric)        Two ColorSpecs + metric enum            Scalar distance         Oklab Euclidean (default), CIEDE2000, WCAG relative luminance ratio

   interpolate(a, b, t, space)   Two colors + t in \[0,1\] + space   Interpolated ColorSpec at t      Linear interpolation in Oklab; or OkLCH for hue-path control

    rotateHue(color, delta_h)    ColorSpec + hue rotation degrees         Rotated ColorSpec                     Rotate (x,y) in Cartesian OkLCH by angle

      scaleChroma(color, k)             ColorSpec + scalar                Scaled ColorSpec                     Scale (x,y) vector; call S2.inGamut() after

    shiftLightness(color, dL)          ColorSpec + L offset               Shifted ColorSpec                            Add dL to z; clamp \[0,1\]

    mix(a, b, mode, weights)     Two colors + blend mode + weights      Composited ColorSpec                         Per-channel blend mode algebra
  ----------------------------- ----------------------------------- ----------------------------- ---------------------------------------------------------------------

**16.3 S2: Gamut and Color Management Service**

  -----------------------------------------------------------------------
          **S2 --- GAMUT & COLOR MANAGEMENT \| Foundation Layer**

  -----------------------------------------------------------------------

A \'reality filter\' that sits alongside the Color Kernel. Ensures every geometric operation produces colors that can actually be displayed in the target output space. No palette enters the rendering pipeline without passing through this service.

  -------------------------------------- ------------------------------------- -------------------------------------------------------------- ------------------------------------------------------------------------------------------------------------------------------------
               **Endpoint**                            **Input**                                         **Output**                                                                                   **Math Foundation**

      inGamut(color, targetProfile)             ColorSpec + profile ID                                    Boolean                                                               Channel-by-channel range check \[0,1\] after profile conversion

   mapToGamut(color, profile, strategy)   ColorSpec + profile + strategy enum                        In-gamut ColorSpec                        Strategies: chroma compress (preferred --- preserves L and h, reduces C only), hue-preserving perceptual scale, clip (last resort)

   paletteGamutReport(palette, profile)          PaletteSpec + profile          Report: out-of-gamut count, worst offenders, suggested fixes                           Per-swatch inGamut check; severity = perceptual distance to nearest in-gamut point
  -------------------------------------- ------------------------------------- -------------------------------------------------------------- ------------------------------------------------------------------------------------------------------------------------------------

**16.4 S3: Palette Geometry Service**

  -----------------------------------------------------------------------
               **S3 --- PALETTE GEOMETRY \| Analysis Layer**

  -----------------------------------------------------------------------

Turns a weighted point cloud into a structured geometric descriptor (Chapters 11 and 14). The full GeometryDescriptor object is this service\'s primary output.

  ---------------------- --------------------------------- ----------------------------------------------------------------------- ------------------------------------------------------------
       **Endpoint**                  **Input**                                           **Output**                                                    **Math Foundation**

   descriptor(palette)       PaletteSpec with weights               Full GeometryDescriptor (all features from Ch. 14.4)            PCA, convex hull, k-means, graph MST, circular statistics

    classify(palette)          Palette or descriptor                            Archetype label + confidence                        Threshold rules on shape scores + hue arc + clusterability

    similarity(p1, p2)      Two palettes or descriptors                      Scalar distance in descriptor space                       Weighted Euclidean on normalized descriptor features

   simplify(palette, k)   Palette + target swatch count k                Reduced palette preserving geometric shape                 k-medoids in Oklab-Cartesian space with weighted sampling

   trajectory(gradient)   Multi-stop gradient definition    Trajectory features: length, curvature, monotonicity, step uniformity      Parametric curve analysis; numerical differentiation
  ---------------------- --------------------------------- ----------------------------------------------------------------------- ------------------------------------------------------------

**16.5 S4: Appearance and Perception Service**

  -----------------------------------------------------------------------
           **S4 --- APPEARANCE & PERCEPTION \| Analysis Layer**

  -----------------------------------------------------------------------

OkLCH coordinates describe color under standard conditions. This service predicts how those coordinates will actually appear under real viewing conditions --- the gap between specification and experience.

  ---------------------------------------------- ------------------------------------- -------------------------------------------------- ---------------------------------------------------------------------
                   **Endpoint**                                **Input**                                   **Output**                                              **Math Foundation**

       predictAppearance(color, conditions)         ColorSpec + viewing conditions      Predicted perceived color under those conditions            CIECAM02 or CAM16; chromatic adaptation transform

       predictSimultaneousContrast(fg, bg)         Foreground + background ColorSpec      Predicted hue shift direction and magnitude      Von Kries chromatic adaptation; opponent channel interaction models

        salience(color, background, size)            ColorSpec + background + area             Predicted pop-out strength \[0,1\]                    Contrast energy model; size-dependent threshold

   legibility(textColor, bgColor, size, weight)   Text + background + typography spec      WCAG ratio + legibility score + pass/fail                WCAG 2.1 relative luminance formula; APCA preview

       predictAdaptation(palette, duration)       Palette + exposure time in minutes        Predicted hue shift of perceived neutral              Chromatic adaptation kinetics; afterimage prediction
  ---------------------------------------------- ------------------------------------- -------------------------------------------------- ---------------------------------------------------------------------

**16.6 S5: Constraint and Safety Service**

  -----------------------------------------------------------------------
            **S5 --- CONSTRAINT & SAFETY \| Validation Layer**

  -----------------------------------------------------------------------

Separates \'beautiful\' from \'usable.\' All hard requirements are encoded here. Nothing passes to the rendering layer without clearing this service.

  ---------------------------- -------------------------------------------- -------------------------------------------------------------------- --------------------------------------------------------------------------
          **Endpoint**                          **Input**                                                **Output**                                                         **Math Foundation**

      checkContrast(theme)      Theme + role assignments + adjacency graph     Pass/fail per role pair + contrast ratios + failing pairs list     WCAG 2.1 formula on all adjacency edges; APCA as optional second opinion

     checkCVD(theme, type)               Theme + simulation type             Simulated appearance + distinguishability scores per critical pair             Brettel/Viénot CVD simulation matrices in LMS space

   checkGamut(theme, target)               Theme + target gamut                          Out-of-gamut swatches + clipping severity                                Channel bounds check after S2 conversion

   repair(theme, constraints)     Failing theme + constraint priorities                Repaired theme with minimal-change adjustments               Constrained optimization; prefer chroma compression over hue changes

         penalty(theme)                 Theme + constraint weights                      Scalar penalty for use in optimization loops                             Weighted sum of all constraint violations
  ---------------------------- -------------------------------------------- -------------------------------------------------------------------- --------------------------------------------------------------------------

**16.7 S6: Semantic Embedding Service**

  -----------------------------------------------------------------------
             **S6 --- SEMANTIC EMBEDDING \| Inference Layer**

  -----------------------------------------------------------------------

The bridge between geometry and meaning. Predicts what a palette communicates and tracks meaning change across transformations.

  ------------------------------------------- ------------------------------------ ------------------------------------------------------------------------------------- -----------------------------------------------------------------
                 **Endpoint**                              **Input**                                                    **Output**                                                              **Math Foundation**

        embedPalette(palette, context)             PaletteSpec + ContextSpec                          MeaningSpec: embedding + VAD + adjective scores                        Hybrid rule-based features + optional learned set encoder

          embedColor(color, context)                ColorSpec + ContextSpec                                      Per-color semantic vector                                       Regression from L, C, h + optional learned model

   scoreKeywords(palette, keywords, context)   Palette + adjective list + context                                Score \[0,1\] per keyword                                Cosine similarity in embedding space; or per-keyword classifier

            drift(p1, p2, context)                Two palette states + context                  Delta-meaning vector + drift magnitude + changed dimensions                    Embedding subtraction + attribution; cosine distance

           explain(palette, context)                   Palette + context            Swatch-level attribution: which swatches contribute most to each semantic dimension        Sensitivity analysis; Shapley-value-style attribution
  ------------------------------------------- ------------------------------------ ------------------------------------------------------------------------------------- -----------------------------------------------------------------

**16.8 S7: Semantic Knowledge Base**

  -----------------------------------------------------------------------
            **S7 --- SEMANTIC KNOWLEDGE BASE \| Memory Layer**

  -----------------------------------------------------------------------

Not ML --- structured memory. Curated knowledge, stored examples, cultural lookup tables, brand anchors, and domain convention rules.

  -------------------------------------- -------------------------------------------- ----------------------------------------------------- ------------------------------------------------------
               **Endpoint**                               **Input**                                        **Output**                                         **Storage / Math**

     lookupByMeaning(query, context)               Semantic query + context                 K nearest palettes with similarity scores             Approximate nearest neighbor (FAISS, HNSW)

       lookupByDomain(domain, task)                   Domain + task type               Convention rules + anchor hues + typical archetypes         Rule tables; lookup by domain/task enum

   storeExample(palette, tags, metrics)   Palette + tags + quality metrics + context              Confirmation; palette indexed                    Append to store; update embedding index

     learnUserProfile(userId, events)             User ID + interaction log                         Updated preference model                          Bayesian update from edit patterns

      getUserBiases(userId, context)                  User ID + context                    User-specific priors over palette features        Probability distribution; used to bias S9 generation
  -------------------------------------- -------------------------------------------- ----------------------------------------------------- ------------------------------------------------------

**16.9 S8: Visual Channel Orchestrator**

  -----------------------------------------------------------------------
        **S8 --- VISUAL CHANNEL ORCHESTRATOR \| Allocation Layer**

  -----------------------------------------------------------------------

Color is one of several visual channels. This service runs before the Assignment Service (S11) and prevents color from being overloaded. It decides which data dimensions get encoded in which visual channels, allocating color alongside size, shape, opacity, motion, and texture.

Available visual channels beyond color: node size, shape marker, opacity, line weight, line style, texture/pattern, spatial position, motion/animation, label typography.

  -------------------------------------------- ------------------------------------------ ----------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------
                  **Endpoint**                                 **Input**                                             **Output**                                                                            **Math Foundation**

   proposeEncodings(data, tasks, constraints)    Data schema + task list + constraints            Encoding plan: data dimension -\> visual channel           Channel capacity: categorical -\> hue (6-8 categories) or shape; ordered -\> L or size; relational -\> position

       evaluateEncoding(encoding, tasks)             Proposed encoding + task list         Confusion rate per task + separability score per dimension pair                         Information-theoretic separability; perceptual confusability models

    allocateChannels(meaningDims, channels)     Semantic dimensions + available channels        Channel allocation minimizing perceptual interference                          Minimize pairwise confusability; greedy allocation by dimension importance
  -------------------------------------------- ------------------------------------------ ----------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------

+:--+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **EDITOR\'S NOTE --- The Over-Encoding Trap**                                                                                                                                                                                                                                                                                                                 |
|   |                                                                                                                                                                                                                                                                                                                                                               |
|   | The single most common failure mode in complex graph visualizations is over-encoding: trying to map 8 data dimensions onto color alone. S8\'s primary job is to refuse this. Color encodes at most 2-3 dimensions cleanly (category by hue, importance by chroma, hierarchy by lightness). Remaining dimensions must go to shape, size, opacity, or position. |
+---+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**16.10 S9: Palette Synthesis Service**

  -----------------------------------------------------------------------
             **S9 --- PALETTE SYNTHESIS \| Generation Layer**

  -----------------------------------------------------------------------

Given a target meaning and a set of constraints, produce palettes. This is the creative core of the platform.

  ----------------------------------------- ------------------------------------------------------------ ------------------------------------------------------------------------ -----------------------------------------------------------------------------------
                **Endpoint**                                         **Input**                                                          **Output**                                                                **Math Foundation**

   generate(targetMeaning, constraints, n)   Target MeaningSpec + ConstraintSet + ContextSpec + count N      N palettes ranked by joint semantic + harmony + constraint score      Multi-objective optimization: CMA-ES or gradient descent in OkLCH-Cartesian space

    mutate(palette, objective, strength)          Palette + objective direction + strength \[0,1\]        Mutated palette with reduced semantic drift on non-targeted dimensions      Gradient-guided move in OkLCH toward objective direction in embedding space

   complete(partialPalette, targetMeaning)       Partial palette with some swatches pinned + target                   Completed palette with free swatches optimized                     Constrained optimization with equality constraints on pinned swatches

    reTheme(theme, mode, preserveMeaning)     Theme + mode (dark/light/high-contrast) + preserve flag       New theme variant; if preserveMeaning, semantic drift is minimized       Geometric operations from Ch. 14 + constraint repair + semantic drift penalty

     interpolateSemantics(p1, p2, steps)                     Two palettes + step count                           Sequence of palettes forming smooth semantic transition              Palette barycenter interpolation in descriptor space; or optimal transport
  ----------------------------------------- ------------------------------------------------------------ ------------------------------------------------------------------------ -----------------------------------------------------------------------------------

**16.11 S10: Spatial Context and Layout-Aware Analysis**

  -----------------------------------------------------------------------
           **S10 --- SPATIAL CONTEXT & LAYOUT \| Context Layer**

  -----------------------------------------------------------------------

Connects the macro geometry of the visualization (node positions, density, occlusion) to color requirements --- without binding to any specific renderer. Provides the adjacency data that S11 Assignment needs for contrast enforcement.

  ------------------------------------------- ---------------------------------------------------------- ------------------------------------------------------------- ---------------------------------------------------------------------
                 **Endpoint**                                         **Input**                                                   **Output**                                                    **Math Foundation**

   adjacencyFromLayout(nodes, edges, params)           Node positions + sizes + edges + camera            Weighted adjacency graph: which nodes appear visually close   Screen-space nearest-neighbor with radius proportional to node size

              densityMap(layout)                                Node positions + sizes                          2D density field over the visualization canvas                       Kernel density estimation in screen space

         occlusionRisk(layout, camera)                        Layout + camera parameters                             Per-node occlusion risk score \[0,1\]                    Depth-sorted overlap estimation; z-buffer approximation

        importanceBudget(graphFeatures)        Graph structure features (degree, centrality, community)               Per-node importance weight \[0,1\]                 Normalize centrality scores; use as palette weight inputs for S11
  ------------------------------------------- ---------------------------------------------------------- ------------------------------------------------------------- ---------------------------------------------------------------------

**16.12 S11: Assignment and Encoding Service**

  -----------------------------------------------------------------------
          **S11 --- ASSIGNMENT & ENCODING \| Application Layer**

  -----------------------------------------------------------------------

The service where palettes meet data. Receives entities and returns a mapping from each entity to a color token. Must scale to thousands of nodes and support incremental updates. Consumes the channel plan from S8 before running its own color optimization.

  ------------------------------------------------------- -------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------
                       **Endpoint**                                                          **Input**                                                                            **Output**                                                                             **Math Foundation**

      assign(entities, palette, constraints, context)      Entity list + palette/theme + ConstraintSet + ContextSpec + adjacency from S10                          AssignmentSpec: entity ID -\> color token                                      See optimization form below; graph coloring + energy minimization

      assignHierarchical(tree, palette, constraints)                        Tree/group structure + palette + constraints                    Hierarchical assignment: parent groups get neutral families; leaves get accent variants                        Top-down assignment with constraint propagation

   assignTemporal(stream, palette, stabilityConstraints)               Streaming entity updates + palette + stability weights                            Updated AssignmentSpec minimizing change from previous frame                          Temporal stability penalty: sum of delta-color magnitudes across frames

               reassignIncremental(changes)                                      Delta of entity attribute changes                                              Partial re-assignment of affected entities only                       Warm-start: reuse previous assignment as initial solution; reoptimize changed neighborhood
  ------------------------------------------------------- -------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------

+:--+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **ASSIGNMENT OPTIMIZATION FORM**                                                                                                                                                                                                                                                                                                                                                             |
|   |                                                                                                                                                                                                                                                                                                                                                                                              |
|   | Minimize over all entity color assignments {c_v}: Sum over edges (u,v) of \[ w_uv \* phi(distance(c_u, c_v)) \] + lambda \* Sum over nodes v of \[ Psi(meaning(c_v), data(v)) \] + constraint_penalty({c_v}). Where: distance is perceptual (Oklab), phi penalizes similar colors on adjacent nodes, Psi ties color meaning to node meaning (from S6), and constraint_penalty comes from S5. |
+---+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**16.13 S12: Rendering and Compositing Service**

  -----------------------------------------------------------------------
            **S12 --- RENDERING & COMPOSITING \| Output Layer**

  -----------------------------------------------------------------------

The last mile. Takes color assignments and scene parameters and verifies that what was specified actually appears correctly in final pixel output.

  ------------------------------------------ ------------------------------------------------------- ----------------------------------------------------------- -------------------------------------------------------------------------------------------------
                 **Endpoint**                                       **Input**                                                **Output**                                                                 **Math Foundation**

       preview(theme, sceneConditions)        Theme + scene (background, lighting, post-processing)             Simulated final appearance + warnings                               Compositing algebra; tone mapping curves; gamma application

       applyToneMapping(colors, curve)                   Color list + tone mapping curve                               Tone-mapped ColorSpecs                                        Tone operator application: Reinhard, ACES, custom sigmoid

   resolveOcclusionContrast(colors, layout)     Color assignments + layout overlap data from S10      Adjusted colors ensuring contrast at occlusion boundaries             Composite appearance of overlapping elements; adjust alpha or L for clarity

   generateEdgeColors(nodeColors, edgeData)       Node color assignments + edge attribute data                         Edge color assignments                     Edge colors: blends of endpoint node colors for flow encoding, or independent with desaturation

    checkFinalContrast(assignment, scene)              Full assignment + scene parameters                Final accessibility check after compositing effects                            Recompute WCAG on composited (not specified) colors
  ------------------------------------------ ------------------------------------------------------- ----------------------------------------------------------- -------------------------------------------------------------------------------------------------

**16.14 S13: Telemetry, Evaluation, and Benchmark Harness**

  -----------------------------------------------------------------------
            **S13 --- TELEMETRY & BENCHMARK \| Learning Layer**

  -----------------------------------------------------------------------

The loop that makes the platform intelligent over time. Without this service, the platform is static. With it, it learns from every interaction, palette edit, and outcome.

  --------------------------------------- --------------------------------------- ---------------------------------------------------------------- ---------------------------------------------------------------------------------
               **Endpoint**                              **Input**                                           **Output**                                                           **Math Foundation**

   logAdjustment(before, after, context)   Before/after palette states + context                 Event stored; model update queued                           Delta encoding between palette states; semantic drift via S6

      inferPreference(userId, events)               User ID + event log                            Updated user preference model                          Bayesian update; or gradient update on learned preference embedding

       recommendNext(palette, goal)               Current palette + goal           Next transformation suggestions ranked by predicted preference   Retrieval from S7 + preference filtering; bandit-style exploration-exploitation

      benchmarkRun(version, suiteId)           Version ID + benchmark suite           Report: per-metric scores + pass/fail per KPI threshold                  Deterministic evaluation suite; compare against baselines

   regressionCheck(newVersion, baseline)              Two version IDs                  Metric deltas + regression alarms for any degradation          Pairwise metric comparison; alert when any KPI drops by declared threshold
  --------------------------------------- --------------------------------------- ---------------------------------------------------------------- ---------------------------------------------------------------------------------

**CHAPTER 17: ADVANCED CONSTRUCTS --- EXTENDED MATHEMATICAL MODELS**

The service architecture covers the buildable core. This chapter maps the extended territory --- mathematical constructs that unlock qualitatively new capabilities when the platform is ready to grow.

**17.1 Palettes as Probability Distributions**

A palette can be represented not as a discrete set of N points but as a probability distribution P over color space --- a mixture of Gaussians or kernel density estimate centered on the swatches.

This unlocks three capabilities:

- Palette barycenters: The \'average\' of two palettes in distribution space, computed via optimal transport (Wasserstein barycenter). Unlike averaging hex values, this gives a geometrically meaningful blend.

- Palette interpolation: A smooth interpolation sequence between two palette styles --- not just between individual colors, but between the underlying color distributions.

- Palette coverage: Measure how well a palette \'covers\' a semantic region of color space --- important for ensuring a system palette has adequate representation of all required meaning dimensions.

Key distance metric: Wasserstein distance (optimal transport) between two palette distributions measures how much \'color mass\' needs to move and how far --- a perceptually meaningful palette difference metric.

**17.2 Semantics as a Field Over Color Space**

Rather than mapping palette to meaning, learn a semantic field: a continuous function f that maps every individual color to its meaning vector, and then integrate over a palette\'s geometry:

m(P) = Sum_i(w_i \* f(c_i)) + Sum\_{i,j}(w_ij \* g(c_i, c_j))

Where f encodes single-color semantics and g encodes pairwise interaction effects (how two colors together shift meaning beyond what either communicates alone).

+:--+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **WHY THIS MATTERS**                                                                                                                                                                                                                                                                                                                                  |
|   |                                                                                                                                                                                                                                                                                                                                                       |
|   | The g term is what captures \'combined effects\' --- that red+black means something different from red+white even when both contain identical red. It\'s the formal representation of Chapter 4\'s claim that palettes are not sums of their parts. Pairwise interactions encoded in g are the theoretical foundation for that empirical observation. |
+---+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

  -------------------------------------------- -------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------------
                 **Component**                                                  **What It Encodes**                                                                       **Training Data**                                                                             **Complexity**

     f(c_i) --- single-color semantic field      Meaning of each color individually; can be precomputed on a grid over color space              Large-scale color-emotion datasets (COLOURlovers, Kuler, Jonauskaite)                              Low --- function of 3 variables; efficient to precompute

   g(c_i, c_j) --- pairwise interaction field   How two specific colors together shift meaning beyond their individual contributions             Two-color combination emotion studies (Ou et al. 2004 and similar)              Medium --- function of 6 variables; parameterize as function of relative L, C, h differences

          w_ij --- interaction weights          How much each pair actually interacts based on area overlap and adjacency in layout    Layout-derived from role-adjacency graph; proportional to shared visual boundary length                        Low --- derived from palette structure and layout
  -------------------------------------------- -------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------------

**17.3 Temporal Stability as a Constraint --- Semantic Inertia**

For dynamic graphs (streaming data, real-time updates), color assignment must balance semantic accuracy against visual stability. Sudden color changes break the user\'s mental model of the visualization.

Formal constraint: add a temporal penalty term to the Assignment Service objective:

Temporal penalty = sum over all nodes v of \[ weight_stability \* distance(c_v(t), c_v(t-1)) \]

Where weight_stability is a tunable parameter that controls the stability-accuracy tradeoff. At high weight_stability, colors barely change between frames. At zero, the assignment is fully re-optimized each frame.

  ------------------ ---------------------------------------------- ------------------------------------------------------------------- ----------------------------------------------------------------------------
     **Strategy**                 **Stability Weight**                                        **When to Use**                                                          **Trade-off**

   Fluid recoloring           0.0 --- no stability penalty           Batch analysis; offline generation; no user observing transitions    Maximum semantic accuracy; potentially jarring if displayed in real-time

     Soft inertia                       0.1--0.3                        Interactive exploration; user is navigating a stable graph           Good semantic accuracy; colors drift gradually rather than jumping

    Strong inertia                      0.5--0.8                       Monitoring dashboards; user has built mental model over time      Colors only change when meaning changes significantly; may lag behind data

    Identity lock     1.0 --- prohibit color changes unless forced       Storytelling; annotated presentations; published reports         Maximum stability; semantic accuracy sacrificed for identity consistency
  ------------------ ---------------------------------------------- ------------------------------------------------------------------- ----------------------------------------------------------------------------

**17.4 Redundancy Encoding --- Never Carry Semantics in Color Alone**

For accessible and information-dense visualizations, critical semantics should always be redundantly encoded across multiple visual channels. This is both an accessibility requirement (CVD users need non-color channels) and a cognitive load principle (multiple encoding channels increase distinguishability under attention constraints).

  -------------------------------- -------------------------------------- -------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------
       **Semantic Dimension**               **Primary Channel**                             **Redundancy Channel(s)**                                                                         **Implementation Notes**

   Community / cluster membership        Hue (qualitative colormap)                      Shape marker + optional texture                  Up to 6-8 hues are pre-attentively distinguishable; shape adds 4-6 more categories; together: up to 48 distinguishable categories

    Node importance / centrality        Chroma (high C = important)                                 Node size                                                   Size and chroma should be positively correlated: larger + more vivid = more important

        Error / alert state              Hue shift to warning color                 Shape change (hexagon / star) + text label                                        Never rely on red-green distinction alone; CVD affects up to 8% of males

             Edge type                  Hue (edge-specific palette)                    Line style (solid / dashed / dotted)                               Edge colors should be visually separated from node colors; use lower chroma or distinct hue range

          Hierarchy level           Lightness L (lower L = deeper level)                   Indentation / size / opacity                                            Lightness ladders work well for 3-5 levels; beyond 5 levels, add size reduction

         Activity / recency               Chroma (active = vivid)          Opacity (stale = transparent) + animation (active = pulsing)                             Motion is highly salient; use sparingly for truly important activity signals
  -------------------------------- -------------------------------------- -------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------

**17.5 The Platform as a Data-to-Pixel Compiler**

The full service stack can be described as a compilation pipeline --- analogous to a programming language compiler, but for visual semantics:

  ----------------------------- ------------------------- ----------------------------------------------------- --------------------------------------------- ------------------------------------------------------------
       **Compiler Stage**           **Analogous to**                      **Platform Service**                                    **Input**                                            **Output**

         Source language            High-level intent      Domain context + emotion target + brand constraints   Human intent: \'calm healthcare dashboard\'            Constraint set + semantic target vector

        Semantic analysis             Type checking             S5 Semantic Embedding + S6 Knowledge Base              Semantic target + domain rules                  Validated semantic specification + priors

   Intermediate representation          AST / IR                   S7 Palette Synthesis + S2 Geometry                    Semantic spec + constraints           Palette object: weighted point cloud + geometry descriptor

          Optimization              Code optimization              S4 Constraint Repair + S7 mutation                       Palette + constraints              Constraint-satisfying palette with minimal semantic drift

         Code generation         Bytecode / machine code                      S8 Assignment                         Palette + entities + graph structure                   Color assignment: entity -\> token

         Target machine               CPU execution                   S10 Rendering + S3 Perception                       Color assignments + scene                Final pixels with compositing corrections applied

            Debugger                Runtime analysis            S11 Telemetry + explain() endpoint of S5                User interactions + outcomes                    Semantic attribution + learning updates
  ----------------------------- ------------------------- ----------------------------------------------------- --------------------------------------------- ------------------------------------------------------------

**CHAPTER 18: SERVICE SUMMARY MATRIX --- ONE-PAGE OVERVIEW**

This chapter is the at-a-glance summary: one row per service, covering its layer, guarantee, primary failure mode, and headline metric. It serves as the navigation layer for Part IV --- for detailed per-service contracts (full input/output schemas, all endpoints, all metrics), see Chapter 20.

+:--+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **HOW TO READ THIS CHAPTER**                                                                                                                                                                                                                                                                             |
|   |                                                                                                                                                                                                                                                                                                          |
|   | Use Chapter 18 to understand what the platform promises as a whole and to quickly locate the service responsible for any given concern. Use Chapter 20 to get the full engineering specification for any individual service. The service numbering S1--S13 is consistent across Chapters 16, 18, and 20. |
+---+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**18.1 Summary Matrix --- Layer and Core Guarantee**

  --------------------------------- ------------- ---------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------
             **Service**              **Layer**                                       **Core Purpose**                                                                            **Must Always Guarantee**

          S1: Color Kernel           Foundation                Color math: conversions, distances, interpolation, transforms                Deterministic outputs; round-trip conversion error \< 1e-4; no NaN or out-of-gamut from safe endpoints

       S2: Gamut & Color Mgmt        Foundation        Reality filter: ensures all colors are displayable in the target output space                No invalid RGB output from mapToGamut(); chroma compression preserves h and L exactly

        S3: Palette Geometry          Analysis     3D shape descriptor: centroid, PCA, hull volume, hue balance, archetype classification           Invariant to swatch ordering; stable under hue wraparound; all shape scores in \[0,1\]

     S4: Appearance & Perception      Analysis       Context-aware appearance: legibility, salience, simultaneous contrast, adaptation            Context is mandatory input; legibility predictions monotonically ordered by WCAG contrast

       S5: Constraint & Safety       Validation            Hard-gate + fixer: WCAG, CVD, gamut compliance + minimal-change repair                   Never claims \'pass\' if any constraint fails; repair only touches non-locked swatches

       S6: Semantic Embedding         Inference          Meaning prediction: VAD affect, adjective scores, semantic drift tracking                 Context is mandatory; embeddings are versioned; drift direction is semantically correct

     S7: Semantic Knowledge Base       Memory                Curated rules, domain priors, brand policies, retrieval by meaning                       Every rule is traceable to a source and version; coverage gaps returned explicitly

   S8: Visual Channel Orchestrator   Allocation        Prevents color overload: allocates data dimensions across all visual channels          No single dimension assigned to two conflicting channels; channel plan is produced before S11 runs

        S9: Palette Synthesis        Generation          Generates and optimizes palettes toward a target meaning under constraints           All candidates pass S5 constraints; candidate set is diverse; infeasibility is reported explicitly

    S10: Spatial Context & Layout      Context          Converts graph layout to weighted adjacency and per-node importance weights                      Adjacency output is symmetric; incremental update \< 50ms for 7k-node graphs

     S11: Assignment & Encoding      Application             Maps palette colors to thousands of entities stably and accessibly              All contrast constraints satisfied; incremental changes minimum entities; stability weight respected

    S12: Rendering & Compositing       Output            Final pixel truth: preview, tone mapping, mismatch detection, edge colors           Mismatch warnings when contrast shifts \> 0.5:1 from spec; pipeline assumptions are always explicit

     S13: Telemetry & Benchmark       Learning             Measures outcomes, runs regressions, updates priors from user feedback           Benchmark suites are versioned and deterministic; regression alarms fire on declared threshold breach
  --------------------------------- ------------- ---------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------

**18.2 Summary Matrix --- Primary Failure Mode and Headline Metric**

  --------------------------------- ---------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------
             **Service**                                             **Most Common Failure Mode**                                                                    **Detection Signal**                                                                **Headline Quality Metric**

          S1: Color Kernel               Gamut creep: chained operations push colors out of gamut without triggering a check                            Assert inGamut() after every non-trivial chain                                Round-trip deltaE error (mean/max over 10k random in-gamut colors)

       S2: Gamut & Color Mgmt              Semantic drift from gamut mapping: chroma compression changes perceived meaning                  Run S6 drift score pre/post mapping; alert if drift exceeds threshold            Mean perceptual delta between pre- and post-mapped colors; semantic drift introduced

        S3: Palette Geometry                  PCA instability for N \< 4 swatches; hull failure on collinear point sets                             Unit tests on edge cases; check for NaN in eigenvalues                           Archetype classification accuracy on expert-labeled test palette set

     S4: Appearance & Perception     Ignoring adaptation: predicting isolated color appearance instead of actual viewing sequence        Track adaptation state as required parameter; A/B test against user reports                     Predictive correlation with user-reported visibility ratings

       S5: Constraint & Safety           Repair local minimum: satisfies constraints but destroys harmony or semantic intent            Monitor S6 drift score after every repair; alert when drift exceeds threshold           Mean perceptual delta from original after repair (smaller = more conservative)

       S6: Semantic Embedding                      Context collapse: domain-specific meanings treated as universal                       Evaluate on held-out domain test sets; check that locale priors are applied             Human alignment: correlation with labeled adjective ratings from human study

     S7: Semantic Knowledge Base                     Stale conventions: rules not updated as design trends evolve                                        TTL metadata on every rule; alert on expiry                                  Rule coverage rate (% of target domains with \>= N curated rules)

   S8: Visual Channel Orchestrator        Channel collision: same data dimension encoded via two correlated visual channels                   Compute inter-channel correlation in proposed plan; flag if \> 0.5                     Task completion accuracy improvement vs baseline (no orchestration)

        S9: Palette Synthesis                           Mode collapse: always generating the same safe palette                        Monitor embedding diversity of output sets; alert if mean pairwise distance drops           Semantic accuracy (embedding distance to target) + candidate set diversity

    S10: Spatial Context & Layout               Layout thrashing: micro-movements trigger full adjacency recomputation              Add stability threshold before flagging adjacency changes; monitor recompute frequency       \% adjacency edges that change between minor layout updates (should be low)

     S11: Assignment & Encoding         Stability oscillation: assignment alternates between two solutions causing flickering               Monitor frame-to-frame color change variance; detect rapid alternation               Contrast compliance rate + % entities changing color per incremental update

    S12: Rendering & Compositing         Post-processing blindness: tone mapping shifts contrast below WCAG without a warning               Compare pre/post tone-mapping WCAG ratios; alert on significant shift                  Final-pixel vs specified contrast delta (mean/max across all role pairs)

     S13: Telemetry & Benchmark              Metric gaming: optimizing acceptance rate at the expense of task performance                          Always track task performance alongside acceptance rate                   Model improvement rate: do telemetry updates improve next-version benchmark scores?
  --------------------------------- ---------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------

**PART IV**

**THE ENGINEERING CONTRACT**

*Canonical Schemas · Full Service Contracts · System-Level KPIs · Integration Interfaces*

*The specifications you hand to engineers. The contracts that keep services interoperable. The metrics that tell you if the platform actually works.*

**CHAPTER 19: CANONICAL DATA SCHEMAS --- THE SHARED LANGUAGE**

Services can only act as services to each other if they speak the same language. These canonical schemas are the typed contracts that every module in the platform must accept and produce. They are the **single source of truth for what a \'color,\' \'palette,\' \'context,\' \'constraint set,\' \'meaning,\' and \'assignment\' actually are** in this system.

+:--+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **CONTRACT PRINCIPLE**                                                                                                                                                                                                                                                                                                                                                                                                                      |
|   |                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|   | A schema is not merely documentation --- it is a validation boundary. Any service that receives a malformed input should reject it explicitly, not silently degrade. Any service that produces output should validate it against the schema before returning. Schema version must be included in every object so embedding comparisons, constraint evaluations, and semantic drift measurements remain comparable across platform releases. |
+---+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**19.1 ColorSpec --- The Atomic Unit**

The fundamental object representing a single color. All services accept and produce ColorSpec. No raw hex strings or bare channel tuples cross service boundaries.

  -------------- ------------- -------------------- --------------------------------------------------------------------- --------------------------------------------------------------------------------
    **Field**      **Type**        **Required**                                **Description**                                                           **Example Values**

      space       enum string          YES                       The color space this color is specified in                \'oklch\' \| \'oklab\' \| \'srgb\' \| \'display-p3\' \| \'xyz-d65\' \| \'hsl\'

        L            float        if OKLCH/Oklab                             Lightness: \[0, 1\]                                                                0.55

        C            float           if OKLCH                               Chroma: \[0, \~0.4\]                                                                0.18

        h            float           if OKLCH                          Hue angle in degrees: \[0, 360)                                                         240.0

        a            float           if Oklab                              Green-red opponent axis                                                             -0.05

        b            float           if Oklab                             Blue-yellow opponent axis                                                            -0.12

   r, g, b_chan      float            if RGB                Normalized linear or gamma-encoded channels: \[0, 1\]                                         0.22, 0.45, 0.89

      alpha          float           \[0, 1\]                    Opacity channel. Default 1.0 (fully opaque)                                                    0.85

     profile        string             YES                            Output profile / target encoding                                   \'srgb\' \| \'display-p3\' \| \'print-iso-coated\'

     metadata       object           optional           Arbitrary key-value annotations: origin, name, tags, version                       { \'name\': \'brand-blue\', \'locked\': true }

   \_cartesian      object      derived (internal)   Cached Cartesian OkLCH coords { x, y, z } for geometry computations                         { x: -0.047, y: -0.175, z: 0.55 }
  -------------- ------------- -------------------- --------------------------------------------------------------------- --------------------------------------------------------------------------------

+:--+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **IMMUTABILITY RULE**                                                                                                                                                                                                                                                                                 |
|   |                                                                                                                                                                                                                                                                                                       |
|   | ColorSpec objects are treated as immutable values, not mutable objects. Every transform produces a new ColorSpec. This ensures that services sharing a reference to the same swatch do not interfere with each other\'s computations --- critical for parallel optimization in the Synthesis Service. |
+---+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**19.2 SwatchSpec --- Color in Context**

A swatch is a color with its role, weight, and constraints. A palette is an ordered collection of swatches.

  ------------- ------------------------- -------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    **Field**           **Type**           **Required**                                                                                                                **Description**

       id                string                YES                                                                      Unique identifier within the palette. Stable across mutations (critical for incremental assignment updates).

      color             ColorSpec              YES                                                                              The color value (see 19.1). Must be specified in OkLCH internally; may carry sRGB for output.

      role             enum string         recommended    \'background\' \| \'surface\' \| \'surface-variant\' \| \'text\' \| \'text-secondary\' \| \'primary\' \| \'secondary\' \| \'accent\' \| \'warning\' \| \'error\' \| \'success\' \| \'info\' \| \'disabled\' \| \'border\' \| \'data-{n}\'

     weight           float \[0,1\]        recommended                                                                       Expected fraction of visual area this swatch occupies. All weights in a palette should sum to 1.0.

   constraints   ConstraintSet (partial)     optional                                                                    Per-swatch overrides: min/max L, locked hue, required contrast vs specific other swatches, CVD requirement.

   provenance            string              optional                                                          \'generated\' \| \'user-defined\' \| \'brand-anchor\' \| \'derived\' \| \'imported\'. Affects how the system handles mutation.
  ------------- ------------------------- -------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**19.3 PaletteSpec --- The Core Object**

  ---------------- -------------------------- -------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
     **Field**              **Type**           **Required**                                                                                        **Description**

         id                  string                YES                                                                                   Globally unique palette identifier.

      version                string                YES                                   Semantic version: \'major.minor.patch\'. Embedding comparisons and drift calculations are only valid within the same major version.

      swatches           SwatchSpec\[\]            YES                                   Ordered list of swatches. The order does not affect geometric computations (which are weight-based) but may affect UI presentation.

     adjacency      EdgeList: \[id, id\]\[\]     optional     Explicit adjacency pairs for swatches that are expected to appear next to each other in the final render. If not provided, the Assignment and Constraint services use role-based defaults.

   structureHints            object              optional                                  { dominant: \[id\...\], accents: \[id\...\] } --- hints about the neutral-backbone + accent structure, used by Geometry Service.

     contextRef     ContextSpec \| contextId   recommended                                                  The context under which this palette was designed or evaluated. Embedded or referenced by ID.

      geometry         GeometryDescriptor        derived                                                       Computed and cached by S2 Palette Geometry Service. Invalidated on any swatch mutation.

      semantic            MeaningSpec            derived                                               Computed and cached by S5 Semantic Embedding Service. Invalidated on swatch mutation or context change.
  ---------------- -------------------------- -------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**19.4 ContextSpec --- The Meaning Conditioner**

Context is what transforms \'a set of colors\' into \'a palette with intent.\' Every semantic prediction and many constraint checks are conditioned on the context. It must travel with every service call that could be context-sensitive.

  -------------------- ------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Field**                           **Type**                                                                                                      **Description**

         medium                              enum                         \'screen-web\' \| \'screen-native\' \| \'print-coated\' \| \'print-uncoated\' \| \'led-billboard\' \| \'vr-headset\' --- affects gamut, rendering, and appearance predictions

       background       ColorSpec \| \'dark\' \| \'light\' \| \'mixed\'                                  The dominant background against which this palette will be perceived. Drives simultaneous contrast predictions.

   ambient_luminance                      float (lux)                                            Approximate viewing environment brightness. Low (5 lux = dark room) to high (50,000 lux = outdoors). Affects appearance model.

          task                               enum                           \'exploration\' \| \'monitoring\' \| \'decision-making\' \| \'storytelling\' \| \'annotation\' \| \'data-entry\' --- shapes semantic priorities and encoding requirements

    audience_locale                     string (BCP-47)                                             Language-culture tag: \'en-US\' \| \'ja-JP\' \| \'pt-BR\'. Drives cross-cultural semantic adjustments from locale priors.

         domain                             string                         \'finance\' \| \'healthcare\' \| \'gaming\' \| \'education\' \| \'creative\' \| \'industrial\' \| \'ecommerce\' \| \... --- conditions meaning priors and convention rules

   brand_constraints                        object                                    { anchor_swatches: SwatchSpec\[\], forbidden_hue_ranges: \[h_min, h_max\]\[\], tone_of_voice: string } --- hard brand locks for S4 Constraint Service

   interaction_policy                       object                                              { states: \[\'hover\',\'focus\',\'selected\',\'disabled\',\'error\'\], motion_allowed: bool, state_transition_duration_ms: int }

   rendering_pipeline                       object                                       { tone_mapping: string, gamma: float, color_grading: object, compositing_mode: string } --- used by S10 Rendering Service for preview accuracy
  -------------------- ------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**19.5 ConstraintSet --- Hard Rules**

  ---------------------- ---------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
        **Field**               **Type**                                                                                   **Description**

      contrast_rules            Rule\[\]         Each rule: { pair: \[roleA, roleB\], min_ratio: float, standard: \'WCAG-AA\'\|\'WCAG-AAA\'\|\'APCA\' }. Applied to all adjacency pairs that match the role pattern.

        cvd_policy                enum                 \'none\' \| \'deuteranopia-safe\' \| \'protanopia-safe\' \| \'tritanopia-safe\' \| \'full-CVD-safe\'. Level of color vision deficiency safety required.

      gamut_targets            string\[\]                                List of required gamut profiles: e.g. \[\'sRGB\', \'P3\'\]. All swatches must be in-gamut for all listed profiles.

          locks                  id\[\]                                                   SwatchSpec IDs that must not be changed by any repair or optimization operation.

        max_colors                int                                              Maximum number of distinct colors in any generated palette or theme. Prevents over-complexity.

      min_separation             float                                               Minimum Oklab Euclidean distance between any pair of adjacent swatches. Prevents collapse.

   forbidden_hue_ranges   \[h_min, h_max\]\[\]                                         Hue angle ranges that must not be used. Applied before and after any optimization step.

    performance_budget           object                                                { max_compute_ms: int, max_api_calls: int } --- for real-time or interactive use cases.
  ---------------------- ---------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

**19.6 MeaningSpec --- The Semantic Output**

  --------------- ------------------------------------------- --------------------------------------------------------------------------------------------------------------------------
     **Field**                     **Type**                                                                        **Description**

     embedding                    float\[d\]                          The learned semantic vector in R\^d. Comparable to other MeaningSpecs only within the same model version.

   model_version                    string                             The version of the semantic model that produced this embedding. Required for cross-palette comparisons.

      affect                        object                                { valence: float\[-1,1\], arousal: float\[-1,1\], dominance: float\[-1,1\] }. PAD/VAD coordinates.

     keywords      { word: string, score: float\[0,1\] }\[\]                        Top-N adjective scores. Include confidence level. Sorted by score descending.

   explanations                   object\[\]                   Optional: { swatch_id: string, contribution_vector: float\[d\], summary: string }. Shapley-style attribution per swatch.

   context_hash                     string                              Hash of the ContextSpec used during embedding. Allows detecting stale embeddings when context changes.
  --------------- ------------------------------------------- --------------------------------------------------------------------------------------------------------------------------

**19.7 AssignmentSpec --- Colors for Entities**

  -------------------- ------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------
       **Field**                                          **Type**                                                                                        **Description**

           id                                              string                                                                           Unique identifier for this assignment state.

        version                                            string                                                              Monotonically increasing version. Incremental updates increment this.

        entries         { entity_id: string, swatch_id: string, token: string, color: ColorSpec }\[\]                 The core mapping: every entity gets a swatch reference, token name, and resolved color.

   stability_metadata         { locked: entity_id\[\], change_budget: float, drift_log: \[\] }              Tracks which entities are locked, what the stability weight was, and which entities changed in this version.

      diagnostics                                        object\[\]                                     { entity_id, contrast_score, separation_score, meaning_alignment, warnings: string\[\] }. Per-entity quality report.

    edge_assignments          { edge_id, color: ColorSpec, opacity: float, style: string }\[\]                     Separate assignments for edges --- cannot be assumed to follow the same token system as nodes.
  -------------------- ------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------

**CHAPTER 20: FULL SERVICE CAPABILITY MATRIX --- 13 PRODUCTION CONTRACTS**

This chapter is the complete engineering contract for all 12 platform services. Each service entry specifies its canonical inputs and outputs (using the schemas from Chapter 19), its hard guarantees (what it must always produce), its primary failure modes, and its quality metrics. This is the document you hand to the engineers implementing each module.

**20.1 S1: Color Kernel**

  -----------------------------------------------------------------------
                          **S1 --- COLOR KERNEL**

  -----------------------------------------------------------------------

  ----------------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Attribute**                                                                                                                                                               **Specification**

      Primary inputs                                                                                                                                          ColorSpec (one or more) + transform operation specification

      Primary outputs                                                                                                                                  ColorSpec (converted, interpolated, or transformed) + error/warning flags

      Hard guarantees      \(1\) Deterministic: same inputs + same version = same outputs. (2) All mapToGamut outputs are verified in-gamut before return. (3) Round-trip conversion error (sRGB -\> OkLCH -\> sRGB) must be below 1e-4 per channel for all colors in \[0,1\]. (4) Hue wrap-around is handled predictably: h is always returned in \[0, 360).

    Must never produce                                                                                         Out-of-gamut colors from \'safe\' endpoints (convert, interpolate). NaN or Infinity in any channel. Different results for same inputs within same version.

   Primary failure modes                                                 Chroma instability near C=0 (hue becomes undefined --- detect and clamp). Gamut creep in chained operations (insert inGamut() check after chains). Precision loss in RGB\<-\>XYZ\<-\>OkLCH round-trips (use 64-bit float internally).

      Quality metrics                                                          Round-trip error (mean/max deltaE over 10k random in-gamut colors). Distance metric symmetry and near-triangle-inequality (spot tests). Batch throughput: ops/sec for 10k color conversions (performance regression gate).
  ----------------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**20.2 S2: Gamut and Color Management**

  -----------------------------------------------------------------------
                    **S2 --- GAMUT & COLOR MANAGEMENT**

  -----------------------------------------------------------------------

  ----------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Attribute**                                                                                                               **Specification**

      Primary inputs                                                                                             ColorSpec + target profile(s) + mapping strategy enum

      Primary outputs                                                                     Gamut validity boolean or report; mapped ColorSpec; palette gamut report with worst-offenders list

      Hard guarantees       \(1\) No valid mapped output has any channel outside \[0, 1\] in the target profile. (2) Mapping strategy is explicit, reproducible, and version-tracked. (3) Chroma compression preserves h and L exactly; only C is reduced.

    Must never produce                                                                           Invalid RGB values (\>1 or \<0) as output of mapToGamut. Silent out-of-gamut return.

   Primary failure modes      Gamut mapping introduces semantic drift (monitor with S5 drift score pre/post mapping). Different device ICC profiles interpret same values differently (require explicit profile specification --- no implicit defaults).

      Quality metrics      \% of generated palettes requiring gamut mapping (lower is better for well-designed synthesis). Mean/max perceptual delta between pre- and post-mapped colors. Semantic drift (MeaningSpec distance) introduced by gamut mapping.
  ----------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**20.3 S3: Palette Geometry**

  -----------------------------------------------------------------------
                        **S3 --- PALETTE GEOMETRY**

  -----------------------------------------------------------------------

  ----------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Attribute**                                                                                                                                                       **Specification**

      Primary inputs                                                                                                                                          PaletteSpec with weights + optional context

      Primary outputs                                                                                            GeometryDescriptor (all features from Ch. 14.4); archetype label + confidence; similarity score between two palettes; reduced palette

      Hard guarantees      \(1\) Invariant to swatch ordering (geometry is computed on the weighted point set, not the ordered list). (2) Stable under hue wraparound (Cartesian conversion is applied before all geometric operations). (3) All shape scores in \[0, 1\]. (4) Same palette + same weights = same descriptor (deterministic).

    Must never produce                                                                                 Archetype labels with confidence \> 0.5 that clearly contradict the eigenvalue pattern. Unstable descriptors from order permutations of the same swatches.

   Primary failure modes                    PCA instability for N \< 4 swatches (eigendecomposition is under-determined --- add fallback for small N). Palettes with many near-identical colors produce \'collapsed\' descriptors (detect and warn). Hull computation failures for degenerate point sets (collinear points).

      Quality metrics                               Descriptor stability: max descriptor distance between same palette with permuted swatch order (must be \~0). Archetype accuracy on labeled test set (human expert labels). Nearest-neighbor retrieval: do geometrically similar palettes feel similar to humans?
  ----------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**20.4 S4: Appearance and Perception**

  -----------------------------------------------------------------------
                    **S4 --- APPEARANCE & PERCEPTION**

  -----------------------------------------------------------------------

  ----------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Attribute**                                                                                                                                                                         **Specification**

      Primary inputs                                                                                                                                     PaletteSpec or ThemeSpec + ContextSpec (background, luminance, typography spec, adjacency)

      Primary outputs                                                                                                                      Legibility scores per role pair; salience scores per swatch; appearance report with risk areas; CVD-simulated palette

      Hard guarantees                                               \(1\) Context is mandatory input --- no context-free appearance predictions. (2) Legibility predictions are monotonically ordered (higher WCAG contrast = higher predicted legibility, all else equal). (3) Provides diagnostics and attribution, not just a score.

    Must never produce                                                                                              Legibility \'pass\' predictions that contradict WCAG for standard (desktop, daylight) viewing conditions. CVD simulations that produce in-gamut-but-invalid results.

   Primary failure modes   Dense visualization emergent effects (small nodes behave differently from large UI blocks --- must parameterize by size). Adaptation effects are context-dependent and easy to ignore (ensure adaptation state is a required input for long-duration UIs). 3D scene lighting invalidates 2D predictions (require explicit scene spec for 3D contexts).

      Quality metrics                                                                          Predictive correlation with user-reported visibility ratings. False positive/negative rate on legibility flags. Runtime under batch evaluation loops (synthesis uses this as an inner loop --- must be fast).
  ----------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**20.5 S5: Constraints and Repair**

  -----------------------------------------------------------------------
                      **S5 --- CONSTRAINTS & REPAIR**

  -----------------------------------------------------------------------

  ----------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Attribute**                                                                                                                                           **Specification**

      Primary inputs                                                                                                        ThemeSpec + ConstraintSet + ContextSpec; or palette + constraints for generation loops

      Primary outputs                                                                                         ConstraintReport (pass/fail per constraint with severity); repaired ThemeSpec; scalar penalty for optimization use

      Hard guarantees       \(1\) Never claims \'pass\' unless all declared constraints are satisfied. (2) Repair only changes non-locked swatches. (3) If repair is infeasible, returns explicit explanation of which constraints conflict. (4) Constraint penalty is monotonically related to violation severity.

    Must never produce                                                                   Themes that pass check() but have actual WCAG failures under standard conditions. False \'CVD-safe\' labels. Repairs that worsen any non-targeted constraint.

   Primary failure modes   Constraint conflicts (brand anchor + contrast requirement + restricted gamut can be infeasible together --- must detect and report gracefully). Repair introduces semantic drift (monitor with S7 embed after repair). Local minimum trap in repair optimization (use multiple restarts).

      Quality metrics            Pass rate of generated candidates pre-repair. Repair success rate (% of failing palettes repaired successfully). Mean perceptual delta from original after repair (smaller = more conservative repair). Semantic drift introduced by repair (MeaningSpec distance pre/post).
  ----------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**20.6 S6: Semantic Embedding**

  -----------------------------------------------------------------------
                       **S6 --- SEMANTIC EMBEDDING**

  -----------------------------------------------------------------------

  ----------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Attribute**                                                                                                                                                              **Specification**

      Primary inputs                                                                                                                     PaletteSpec + ContextSpec (mandatory); keyword list for scoring; two palettes for drift measurement

      Primary outputs                                                                                               MeaningSpec (embedding vector, VAD affect coordinates, keyword scores, explanations); drift delta between two states; per-swatch attribution

      Hard guarantees      \(1\) Context is mandatory --- no context-free embeddings. (2) Embeddings are versioned --- comparisons across versions are flagged. (3) Drift direction is semantically correct (moving toward \'calm\' geometry does not increase arousal prediction). (4) Same palette + same context + same model version = same embedding.

    Must never produce                                                       Embeddings that violate known directional relationships (high chroma predicting lower arousal). Context-free predictions on context-sensitive inputs. Cross-version embedding comparisons without version mismatch warning.

   Primary failure modes                Context collapse (treating universal what is domain-specific --- enforce context conditioning). Out-of-distribution palettes (very unusual geometries produce overconfident labels --- add confidence scores). Cultural mismatch (locale differences require separate prior calibration per locale).

      Quality metrics            Human alignment: correlation with labeled adjective ratings from human study. Retrieval precision/recall: \'find palettes matching keyword X.\' Drift sensitivity: meaning-preserving transforms produce drift below threshold epsilon. Embedding stability (same palette, multiple model calls = same embedding).
  ----------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**20.7 S7: Semantic Knowledge Base**

  -----------------------------------------------------------------------
                    **S7 --- SEMANTIC KNOWLEDGE BASE**

  -----------------------------------------------------------------------

  ----------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Attribute**                                                                                                                                    **Specification**

      Primary inputs                                                                                 Semantic queries (keywords, affect range, embedding); domain + task for convention lookup; palettes + tags for storage

      Primary outputs                                                                              Matching palette examples with similarity scores; domain convention rules; brand policies; meaning priors per locale/domain

      Hard guarantees       \(1\) Traceability: every rule has a source, owner, and version. (2) Separation of \'editorial truths\' (curated human rules) from \'learned guesses\' (model-generated priors). (3) Brand anchors returned by brandPolicy() are valid ColorSpecs in the stated profile.

    Must never produce                                                            Untraceable rules with no source. Conflicting rules for the same domain without conflict resolution policy. Stale rules beyond declared TTL without warning.

   Primary failure modes   Rule conflicts across brands/domains (require explicit resolution priority). Stale conventions as design trends evolve (require TTL metadata on every rule). Coverage gaps (no rules for a new domain --- return explicit \'no coverage\' rather than defaulting silently).

      Quality metrics                     Domain coverage rate (% of target domains with at least N curated rules). Rule conflict rate (% of rule pairs that produce contradictory guidance). Retrieval usefulness (adoption rate: % of retrieved examples that users keep vs discard).
  ----------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**20.8 S8: Visual Channel Orchestrator**

  -----------------------------------------------------------------------
                  **S8 --- VISUAL CHANNEL ORCHESTRATOR**

  -----------------------------------------------------------------------

Runs before the Assignment Service (S11) and determines which data dimensions are encoded in which visual channels. Its output --- the channel allocation plan --- is a required input to S11.

  ----------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Attribute**                                                                                                                                                                                                  **Specification**

      Primary inputs                                                                                                                                                                   Data schema (attribute names + types) + task list + ConstraintSet + ContextSpec

      Primary outputs                                                                                                                                             Channel allocation plan: { data_dimension -\> visual_channel }\[\] + separability scores per allocation; conflict warnings

      Hard guarantees                                                                    \(1\) No data dimension is simultaneously encoded in two correlated visual channels. (2) Color is allocated at most 2-3 data dimensions (category by hue, magnitude by L, importance by C). (3) Every channel in the plan is realizable in the declared rendering pipeline.

    Must never produce                                                                                       Plans that assign a categorical dimension with \> 8 categories to hue alone (beyond pre-attentive discriminability). Plans that leave accessibility-critical dimensions encoded only in color without a redundant non-color channel.

   Primary failure modes   Channel collision: two data dimensions correlated with each other assigned to correlated visual channels, wasting one channel (detect by computing inter-dimension correlation matrix). Accessibility gap: CVD-critical distinctions assigned to hue with no shape or label fallback. Overcrowding: more dimensions allocated than channels can cleanly carry --- must return explicit capacity warning.

      Quality metrics                                                                     Task completion accuracy improvement vs no orchestration (user study). Channel utilization rate: % of available channels actually used (unused channels = wasted discriminability). Confusion rate reduction: pre/post-orchestration confusion on critical category pairs.
  ----------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**20.9 S9: Palette Synthesis**

  -----------------------------------------------------------------------
                       **S9 --- PALETTE SYNTHESIS**

  -----------------------------------------------------------------------

  ----------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Attribute**                                                                                                                                                                                               **Specification**

      Primary inputs                                                                                                                                       Target MeaningSpec (or keywords + affect target) + ConstraintSet + ContextSpec + optionally a seed palette; number of candidates N

      Primary outputs                                                                                                                                              CandidateSet: N PaletteSpecs each with semantic score, constraint report, geometry descriptor, and diversity rank

      Hard guarantees                          \(1\) All candidates in CandidateSet pass constraint checks from S5. (2) Candidate set is diverse: pairwise mean embedding distance must exceed a minimum threshold. (3) Every candidate includes scoring diagnostics explaining why it was selected. (4) If constraints are unsatisfiable, returns an explicit infeasibility report --- not an empty set.

    Must never produce                                                                                                    Candidates that violate hard constraints. Sets with all near-identical candidates (mode collapse). Candidates that score lower on the semantic target than a random palette from the knowledge base.

   Primary failure modes   Mode collapse (always generating safe, boring palettes --- monitor embedding diversity of output sets). Semantic hacking (model finds unusual colors that score well on the embedding without looking intentional --- add perceptual sanity checks). Constraint-semantic conflict (target meaning requires colors that violate hard constraints --- return graceful degradation with explanation).

      Quality metrics                           Constraint satisfaction rate (% candidates passing all checks). Semantic accuracy (embedding distance to target, lower is better). Candidate diversity (mean pairwise embedding distance in output set). Compute cost per candidate (interactive: \< 200ms per candidate). Human preference rate on generated vs human-designed palettes for same brief.
  ----------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**20.10 S10: Spatial Context and Layout-Aware Analysis**

  -----------------------------------------------------------------------
                   **S10 --- SPATIAL CONTEXT & LAYOUT**

  -----------------------------------------------------------------------

  ----------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Attribute**                                                                                                                                                                                              **Specification**

      Primary inputs                                                                                                                                                           Graph layout: node positions + sizes + edge list + camera parameters + interaction state

      Primary outputs                                                                                                                                      Weighted adjacency graph (which nodes appear visually close); density field; per-node occlusion risk; per-node importance weight

      Hard guarantees                                                                                          \(1\) Output is stable under small layout perturbations (avoids triggering full re-assignment on micro-movements). (2) Scales to 7,000+ nodes with incremental updates. (3) adjacencyFromLayout() outputs are symmetric.

    Must never produce                                                                                                                          Asymmetric adjacency relationships. Importance weights outside \[0, 1\]. Complete recomputation output when only an incremental update was requested.

   Primary failure modes   Layout thrashing: frequent small layout changes invalidate adjacency too often --- add a stability threshold before flagging changes. Over-simplified adjacency: screen-space nearest-neighbor approximation misses visual neighbors at node periphery --- parameterize radius appropriately. Zoom level changes radically alter adjacency --- must be re-run when camera changes significantly.

      Quality metrics                                                                                 Runtime for 7k-node graph: full computation \< 500ms; incremental \< 50ms. Adjacency accuracy vs actual screen-space neighbors (sampled evaluation). Stability ratio: % of edges that change between minor layout updates (should be low).
  ----------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**20.11 S11: Assignment and Encoding**

  -----------------------------------------------------------------------
                     **S11 --- ASSIGNMENT & ENCODING**

  -----------------------------------------------------------------------

  ----------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Attribute**                                                                                                                                                                                                                                            **Specification**

      Primary inputs                                                                                                                                                               Entity list with feature attributes + PaletteSpec or ThemeSpec + ConstraintSet + ContextSpec + layout adjacency (from S9) + optional prior AssignmentSpec (for incremental)

      Primary outputs                                                                                                                                                                              AssignmentSpec (entity -\> token/color) + per-entity diagnostics (contrast, separation, meaning alignment) + edge assignment recommendations

      Hard guarantees                                                   \(1\) All declared contrast constraints on adjacency pairs are satisfied. (2) At least one valid assignment exists and is returned if constraints are satisfiable. (3) Incremental updates change the minimum number of entities necessary. (4) Stability weight is applied: no entity changes color unless the new assignment exceeds old quality by the margin declared in stabilityConstraints.

    Must never produce                                                                                                                                    Assignments where any declared role pair violates WCAG contrast requirement. Complete re-assignments on minor data changes when incremental mode is requested. Assignments with adjacent nodes below min_separation threshold.

   Primary failure modes   Color graph pressure (insufficient distinguishable colors for the topology --- detect infeasibility and report which node groups cannot be separated). Category overload (more categories than human pre-attentive discriminability allows --- S9 Channel Orchestrator should have caught this upstream). Stability oscillation: assignment alternates between two equally good solutions causing flickering (add hysteresis: new assignment accepted only if quality gain exceeds epsilon).

      Quality metrics                                                          Contrast compliance rate (% role pairs meeting declared thresholds). Separation quality (distribution of perceptual distances between adjacent node pairs). Cluster consistency (within-cluster cohesion vs between-cluster separation ratio). Stability: % entities whose color changes per incremental update. User task performance (search time, error rate on pattern finding).
  ----------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**20.12 S12: Rendering and Preview Truth**

  -----------------------------------------------------------------------
                   **S12 --- RENDERING & PREVIEW TRUTH**

  -----------------------------------------------------------------------

  ----------------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Attribute**                                                                                                                                                                                                   **Specification**

      Primary inputs                                                                                                                                          AssignmentSpec + ThemeSpec + render settings (tone mapping curve, gamma, background, lighting model, compositing mode) + ContextSpec

      Primary outputs                                                                                                                             Preview image or rendered frame; mismatch report comparing specified-vs-rendered contrast; suggested compensation adjustments; final contrast check results

      Hard guarantees                                      \(1\) Preview is faithful to the declared pipeline settings --- no implicit assumptions about gamma or color space. (2) Mismatch diagnostics are provided whenever final-pixel contrast deviates more than 0.5:1 from the specified WCAG ratio. (3) Edge color generation does not create interference patterns with adjacent node colors.

    Must never produce                                                                                                                                 Silent failures where post-processing shifts contrast below WCAG without a warning. Preview images produced under undeclared pipeline assumptions.

   Primary failure modes   Post-processing blindness (tone mapping, color grading, or bloom applied after assignment invalidates color semantics --- must model the full pipeline). Cross-platform inconsistency (web vs native vs GPU render different final colors for same spec --- parameterize by platform). Dense scene emergent contrast (many overlapping elements create visual noise that individual pairwise checks miss).

      Quality metrics                                                               Final-pixel vs specified contrast delta (mean, max across all role pairs). Platform consistency: max Oklab distance between same assigned color rendered on different target platforms. Mismatch detection rate (% of significant post-processing color shifts that trigger a warning).
  ----------------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**20.13 S13: Telemetry, Evaluation and Benchmark Harness**

  -----------------------------------------------------------------------
                     **S13 --- TELEMETRY & BENCHMARK**

  -----------------------------------------------------------------------

  ----------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       **Attribute**                                                                                                                                                                                             **Specification**

      Primary inputs                                                                                                                     User interaction events (edits, accept/reject, time-on-task); palette versions before/after; benchmark suite ID and version; model version for regression testing

      Primary outputs                                                                                                                                      Event log; benchmark reports with per-metric scores; regression deltas between versions; optional prior updates for S6 and S8

      Hard guarantees                                                      \(1\) Reproducibility: benchmark suites are versioned and deterministic. (2) Privacy boundary is explicit: what is stored, what is anonymized, TTL per event type. (3) Regression alarms are generated when any tracked metric degrades by more than the declared threshold between versions.

    Must never produce                                                                                                              Benchmark results that are not version-tagged. Non-deterministic benchmark outcomes on the same versioned suite. Data stored beyond TTL without explicit retention policy.

   Primary failure modes                          Metric gaming (optimizing for user acceptance rate at the expense of task performance --- always measure both). Feedback loops biasing toward \'safe boring palettes\' (monitor diversity and novelty metrics alongside acceptance). Cold-start problem (new users have no history --- benchmark should include a cold-start quality baseline).

      Quality metrics      Palette acceptance rate (necessary but not sufficient). Task performance metrics (search time, error rate, confusion rate in user studies). Semantic and contrast regression per release (tracked in benchmark suite). Diversity and novelty metrics over generated outputs (prevent library convergence). Model improvement rate: does telemetry data improve next-version benchmark scores?
  ----------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**CHAPTER 21: SYSTEM-LEVEL KPIs --- THE DEFINITION OF DONE**

Individual service metrics tell you if a module works. System-level KPIs tell you if the platform delivers on its promise. These are the numbers a technical lead should review before every production release and that benchmark suites should run automatically on every merge.

**21.1 The Five System Dimensions**

  -------------------------- ------------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------------------------------
   **System KPI Dimension**                                              **What It Measures**                                                                                                        **Why It Matters**                                                                            **Benchmark Frequency**

      Semantic Stability                        How much meaning changes during transforms that should preserve meaning                     A palette engine that changes what it communicates when you adjust contrast or switch to dark mode is useless for intentional design            Every release; continuous regression

   Constraint Satisfaction                   \% of generated and repaired palettes that pass all declared hard constraints                                        Hard requirements (WCAG, CVD, gamut) are non-negotiable; any failure is a production bug                                   Every PR; zero-tolerance regression

    Separability at Scale                            How well colors distinguish adjacent entities in large graphs                                        For 7,000+ node visualizations, the assignment problem is the hardest test of the system\'s core promise                    Every release; with standardized graph topologies

      Temporal Stability                          How much color assignment changes frame-to-frame in dynamic graphs                                                     Visual flickering destroys user cognition; stability must be controllable                                    Integration test with streaming graph simulation

    Diversity and Novelty     How varied the generated palette candidates are; does the library avoid converging on the same safe answers                       A palette engine that always produces the same 10 palettes is a lookup table, not an engine                        Weekly; with diversity metrics on recent generation log
  -------------------------- ------------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------------------------------

**21.2 Semantic Stability --- Detailed Specification**

Definition: given a palette P and a set of \'meaning-preserving transforms\' T (hue rotation within 30 degrees, dark-mode adaptation, accessible contrast repair, chroma scale by factor 0.8), the maximum semantic drift across all T must be below a threshold.

Semantic drift = distance(embed(P), embed(T(P))) in the MeaningSpec embedding space

  ------------------------------------------- -------------------------------------------- --------------------------------------------------- -------------------------------------------------------------------
              **Transform Type**               **Max Allowed Drift (embedding distance)**          **Max Allowed Keyword Rank Change**                         **Max Allowed VAD shift per axis**

      Hue rotation within +/- 30 degrees              0.05 (5% of embedding range)                Top-3 keywords must remain identical                                    0.05 per axis

            Dark-mode L adaptation                                0.10                      Top-3 keywords may change at most 1 rank position                             0.10 per axis

   Accessible contrast repair (C adjustment)                      0.08                            Top-3 keywords must remain identical                                    0.08 per axis

      Chroma scaling 0.8x (desaturation)                          0.15                             Top-5 keywords must remain in top-5          Arousal may decrease up to 0.15; Pleasure may decrease up to 0.10

            Full dark-mode re-theme                               0.20                             Top-5 keywords must remain in top-5                                    0.20 per axis
  ------------------------------------------- -------------------------------------------- --------------------------------------------------- -------------------------------------------------------------------

**21.3 Constraint Satisfaction --- Detailed Specification**

  --------------------------------------------------- --------------------------------------------------------------------------- ---------------------------------------------------------------------- ---------------------------------------------------------
                **Constraint Category**                                         **Required Pass Rate**                                                   **Zero-Tolerance Cases**                                             **Measurement**

         WCAG AA contrast (text on background)                     100% of declared role pairs in released palettes                         Any text-on-background failure is a production bug                Automated: WCAG formula on all adjacency pairs

           WCAG AA contrast (UI components)                        100% of declared role pairs in released palettes                        Icon and button border failures are production bugs                Automated: WCAG formula on component role pairs

   CVD distinguishability (when CVD policy declared)   100% of critical role pairs distinguishable under declared CVD simulation    Safety-critical colors (warning, error) must never merge under CVD     Automated: Brettel/Vienot simulation + distance check

     Gamut validity (all declared target profiles)           100% of released swatches in-gamut for all declared profiles           Any out-of-gamut swatch in a released palette is a production bug     Automated: channel range check after profile conversion

                  Repair success rate                              \> 95% of failing palettes successfully repaired                5% unsatisfiable cases must receive explicit infeasibility diagnosis            Automated: repair + re-check pipeline
  --------------------------------------------------- --------------------------------------------------------------------------- ---------------------------------------------------------------------- ---------------------------------------------------------

**21.4 Separability at Scale --- Detailed Specification**

Test suite: run S10 Assignment on three standardized graph topologies of N=500, N=2000, and N=7000 nodes.

  ------------------------------------------- ------------------------------------------ --------------------- ----------------------------------- -----------------------------------------------------------
                  **Metric**                                  **N=500**                       **N=2000**                   **N=7000**                                    **Measurement**

     Min adjacent-node perceptual distance               \> 0.12 Oklab units              \> 0.12 Oklab units          \> 0.10 Oklab units          Min distance across all adjacent node pairs in assignment

      Mean within-cluster color cohesion                 \> 0.70 (normalized)                   \> 0.65                      \> 0.60                Mean intra-cluster distance / mean inter-cluster distance

   Edge readability (edge vs node contrast)    \> 3:1 WCAG ratio for edge-on-background         \> 3:1          \> 2.5:1 (dense layout tolerance)   WCAG contrast: edge color vs background at edge midpoint

            Assignment compute time                            \< 200ms                        \< 800ms                     \< 3000ms                 Wall clock time for full assignment (not incremental)

   Incremental update time (10% node change)                   \< 20ms                          \< 80ms                     \< 200ms                      Wall clock time for incremental reassignment
  ------------------------------------------- ------------------------------------------ --------------------- ----------------------------------- -----------------------------------------------------------

**21.5 Temporal Stability --- Detailed Specification**

  --------------------------------- ------------------------------------------------------------------------ ------------------------------------------------------------------------------------- ----------------------------------
         **Stability Mode**                              **Max Color Churn Per Update**                                                 **Max Flicker Detection Rate**                                       **Definition**

    Soft inertia (weight 0.1-0.3)    \< 20% of entities change color per update when \< 10% of data changes   \< 5% of 2-frame windows show the same entity changing twice in opposite directions      Standard interactive mode

   Strong inertia (weight 0.5-0.8)                   \< 5% change when \< 10% data changes                                                    \< 1% flicker rate                                       Monitoring dashboard mode

     Identity lock (weight 1.0)                0% change unless semantic violation forces update                                                  0% flicker                                        Storytelling / presentation mode
  --------------------------------- ------------------------------------------------------------------------ ------------------------------------------------------------------------------------- ----------------------------------

**21.6 Diversity and Novelty --- Detailed Specification**

  ------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------- ------------------------------------------------------------------------
            **Metric**                                                                          **Target Value**                                                                                                 **Measurement**                                                         **Failure Mode It Prevents**

   Candidate set intra-diversity                                      Mean pairwise embedding distance in any generate() output set \> 0.15                                        Compute mean pairwise distance among N candidates after each generate() call            Mode collapse: all candidates are the same safe palette

    Library archetype coverage     At least 4 of the 6 canonical archetypes (Needle, Fan, Bipolar, Neutral Spine, Helix, Cloud) represented in any 50-palette generation batch   Classify each generated palette with S3 classify(); count archetype distribution   Topology collapse: library only contains one type of palette structure

       Semantic novelty rate                         \> 30% of generated candidates have embedding distance \> 0.20 from all existing knowledge base entries                     Check each candidate against full knowledge base via S7 nearest-neighbor search        Generation degenerates to retrieval: no new territory explored

       Cross-domain transfer                                       \> 60% accuracy when generating for a new domain using only 5 seed examples                                                  Held-out domain evaluation with few-shot prompting                         Domain overfitting: model only works for trained domains
  ------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------- ------------------------------------------------------------------------

**CHAPTER 22: INTEGRATION INTERFACES --- CONNECTING TO THE OUTSIDE WORLD**

The platform\'s internal services communicate through the canonical schemas of Chapter 19. This chapter defines the stable external interfaces --- the minimal, clean boundaries between the platform and whatever visualization engine, renderer, design tool, or application is consuming it.

+:--+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|   | **ARCHITECTURE PRINCIPLE**                                                                                                                                                                                                                                                                                                                                        |
|   |                                                                                                                                                                                                                                                                                                                                                                   |
|   | The platform must have no knowledge of the specific visualization type that consumes it. It does not know if it is coloring a graph, a UI, a data dashboard, or a physical environment. The consumer provides entities and context; the platform returns assignments and diagnostics. This is the boundary that makes the platform reusable across product lines. |
+---+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**22.1 Inputs the Platform Receives from Any Consumer**

  --------------------------------------- ---------------------------------------------------------------------------------------------- --------------------------------- --------------------------------------------------------------------------------------------------------------
            **Input Category**                                                      **Schema**                                                     **Required**                                                  **What the Platform Does With It**

        Entity list with attributes        { entity_id: string, attributes: { cluster: string, value: float, status: enum, \... } }\[\]                 YES                      Feeds S10 Assignment: drives data-to-geometry mappings; determines category count for color budget

         Layout context (optional)            { node_positions: \[id, x, y, z\]\[\], node_sizes: \[id, float\]\[\], camera: object }         Optional but recommended                   Feeds S9 Spatial Context: builds weighted adjacency graph for contrast requirements

          Rendering pipeline spec                   Part of ContextSpec: tone_mapping, gamma, compositing_mode, target_profile                 Strongly recommended                             Feeds S11 Rendering: enables accurate preview and mismatch detection

         Interaction state policy                     Part of ContextSpec: states list, motion_allowed, transition_durations              Recommended for interactive use            Feeds S10 Assignment: triggers state-layer expansion (hover, selected, disabled variants)

         Brand and domain context                     Part of ContextSpec: domain, audience_locale, brand_constraints, task                    Strongly recommended         Feeds S6 Semantic, S7 Knowledge Base, S8 Synthesis: conditions all meaning predictions and generation priors

        Semantic intent (optional)                   Target MeaningSpec (keywords or affect vector) + palette seed (optional)                        Optional                        Feeds S8 Synthesis: if not provided, platform uses domain defaults + knowledge base priors

   Stability policy (for dynamic graphs)            { stability_weight: float, locked_entities: id\[\], change_budget: float }              Required for streaming use            Feeds S10 Assignment incremental mode: controls temporal stability vs semantic accuracy tradeoff
  --------------------------------------- ---------------------------------------------------------------------------------------------- --------------------------------- --------------------------------------------------------------------------------------------------------------

**22.2 Outputs the Platform Provides to Any Consumer**

  ------------------------------------- --------------------------------------------------------------------------------------------------- ----------------------------------------------------------------------------- ---------------------------------------------------------------------------------------------
               **Output**                                                           **Schema**                                                                             **Primary Use**                                                                 **Consumer Responsibility**

        ThemeSpec (token system)         { token: string, color: ColorSpec, role: string, state_variants: { hover: ColorSpec, \... } }\[\]   Static palette application: CSS variables, design tokens, component theming   Consumer maps token names to their component system; platform does not know component names

   AssignmentSpec (entity assignments)                                   Full AssignmentSpec from Ch. 19.7                                             Dynamic coloring: graph nodes, data points, list items               Consumer reads entity_id -\> color and applies it during render; manages rendering layer

     Edge assignment recommendations                               Part of AssignmentSpec: edge_assignments\[\]                                           Edge colors, opacity, line styles for graph edges                     Consumer decides final line rendering; platform provides semantic recommendations

           Diagnostic overlays                       { entity_id, warnings: string\[\], contrast_score, separation_score }\[\]                                       Debugging, QA, editor tools                                   Consumer decides whether to display diagnostics; platform provides the data

             Preview images                                         From S11: rendered image + mismatch report                                               Design tool integration, approval workflows                      Consumer requests preview with their pipeline spec; platform renders and flags issues

             Semantic report                                         MeaningSpec for the full assignment state                                      Brand review, accessibility audit, stakeholder communication                       Consumer formats and presents; platform provides the semantic data
  ------------------------------------- --------------------------------------------------------------------------------------------------- ----------------------------------------------------------------------------- ---------------------------------------------------------------------------------------------

**22.3 Feedback the Consumer Sends Back**

  -------------------------- ----------------------------------------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      **Feedback Type**                                                **Schema**                                                                                                                                **What the Platform Learns**

       Manual override            { entity_id, old_color: ColorSpec, new_color: ColorSpec, reason: string (optional) }        S12 Telemetry: logs the override. S7 Knowledge Base: if same override pattern appears \> N times, it becomes a new prior. S8 Synthesis: biases future generation away from the overridden solution.

    Accept / reject signal                { palette_id, action: \'accept\'\|\'reject\', context: ContextSpec }                                               S12 Telemetry: updates user preference model in S7 Knowledge Base. S8 Synthesis: adjusts generation priors toward accepted palettes.

   Task performance metrics                       { task_type, time_ms, error_count, confusion_report }                                           S12 Benchmark: updates task performance scores. Does not update semantic model directly --- requires human review before incorporation as training signal.

     Explicit annotation      { palette_id, adjectives: string\[\], affect: VAD, quality: float\[0,1\], annotator: userId }                                              S6 Semantic Embedding: highest quality training signal for model improvement. Version-tagged and attributed.
  -------------------------- ----------------------------------------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**22.4 What the Platform Deliberately Does Not Control**

Specifying what is outside the platform\'s scope is as important as specifying what is inside it. The following are the consumer\'s responsibility, not the platform\'s:

- Node and edge rendering: the visual shape, size, and position of graph elements. The platform provides colors; the renderer applies them.

- Layout algorithms: how nodes are positioned in 2D or 3D space. The platform receives layout data from S9 but does not compute layouts.

- Typography: font choice, weight, and size. The platform provides text-color and background-color tokens with contrast guarantees; the consumer controls font rendering.

- Animation and motion beyond color: the platform may recommend transition durations for color state changes; all other motion is the consumer\'s domain.

- User interaction logic: hover detection, click handling, selection state management. The platform provides state-variant colors; the consumer manages state transitions.

- Data aggregation and graph structure computation: the platform receives graph data; it does not compute communities, centrality, or layout.

**22.5 Minimal Viable Integration (One-Page Spec)**

For a consumer that wants to integrate the platform at minimum viable complexity, the required interface reduces to:

  ------------------------ ----------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------- -----------------------------------------------------------------
          **Step**                                         **Consumer Action**                                                                    **Platform Response**                                                            **Required Inputs**

       1\. Initialize       Send ContextSpec with domain, locale, task, brand constraints, rendering pipeline                  Platform loads domain priors, brand policy, rendering models                             ContextSpec (at minimum: domain + medium)

    2\. Request palette             Send target meaning or accept domain defaults; send ConstraintSet           Platform runs S8 Synthesis -\> S5 Constraint check -\> return top-3 candidates with scores               ConstraintSet (at minimum: WCAG level)

     3\. Select palette               Accept one candidate; optionally override individual swatches                    Platform stores selection in S7 Knowledge Base; overrides are logged in S12                     Selection signal + any SwatchSpec overrides

   4\. Request assignment           Send entity list with attributes; optionally send layout context                          Platform runs S9 -\> S10 Assignment -\> return AssignmentSpec                  Entity list; ConstraintSet from step 2; ContextSpec from step 1

    5\. Apply and render        Apply AssignmentSpec to render; send rendering pipeline spec for preview                 Platform runs S11 preview; returns mismatch warnings if contrast shifts                      RenderSpec (tone mapping, gamma, background)

     6\. Send feedback                   Log accepts/rejects/overrides as they occur during use                   Platform updates user profile; incorporates high-quality feedback into training queue       Feedback events (accept/reject minimum; annotations optional)
  ------------------------ ----------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------- -----------------------------------------------------------------

**APPENDIX A: QUICK REFERENCE TABLES**

**A.1 OkLCH → Semantic Mapping Priors**

Use these as starting priors for a rule-based semantic engine, before data-driven refinement:

  -------------------- ----------------------------- --------------------------------------------------------- -----------------------------------------------
   **OkLCH Property**         **Value Range**                        **Predicted PAD Effect**                           **Typical Adjective Cluster**

     L (Lightness)         0.0--0.25 (very dark)          Valence: ↓ moderate, Arousal: ↓, Dominance: ↑↑        dramatic, serious, heavy, depth, night, power

     L (Lightness)       0.25--0.50 (medium-dark)     Valence: neutral, Arousal: neutral, Dominance: moderate       solid, grounded, professional, mature

     L (Lightness)       0.50--0.75 (medium-light)          Valence: ↑, Arousal: moderate, Dominance: ↓         friendly, approachable, clear, open, balanced

     L (Lightness)        0.75--1.0 (very light)              Valence: ↑↑, Arousal: ↓, Dominance: ↓↓             airy, minimal, clean, soft, delicate, pure

       C (Chroma)       0.0--0.05 (near achromatic)                Arousal: ↓↓, Valence: neutral                    neutral, corporate, serious, minimal

       C (Chroma)           0.05--0.15 (muted)                     Arousal: ↓, Valence: slight ↑                 subtle, refined, sophisticated, restrained

       C (Chroma)          0.15--0.25 (moderate)                   Arousal: moderate, Valence: ↑                     balanced, confident, clear, branded

       C (Chroma)           0.25--0.40+ (vivid)          Arousal: ↑↑, Valence: ↑ or ↓ (context dependent)        energetic, bold, playful, vibrant, intense

        h° (Hue)          330°--30° (red-orange)        Temperature: very warm; cultural: appetite, urgency         action, energy, food, danger, passion

        h° (Hue)         30°--90° (orange-yellow)         Temperature: warm; cultural: optimism, caution        optimistic, sunny, playful, warning, cheerful

        h° (Hue)         90°--165° (yellow-green)         Temperature: neutral; cultural: nature, growth             natural, eco, fresh, growth, health

        h° (Hue)          165°--255° (green-blue)            Temperature: cool; cultural: trust, calm             calm, trustworthy, tech, clinical, water

        h° (Hue)         255°--330° (blue-violet)      Temperature: very cool; cultural: premium, creativity    luxury, premium, creative, mysterious, royal
  -------------------- ----------------------------- --------------------------------------------------------- -----------------------------------------------

**A.2 WCAG Contrast Requirements Reference**

  ---------------- -------------------------------------- ---------------------------- ---------------------------------------------------------------
   **WCAG Level**              **Text Type**               **Minimum Contrast Ratio**                           **Use Case**

    AA (Minimum)    Normal text (\< 18pt / \< 14pt bold)             4.5:1                     Standard body text, UI labels, default minimum

    AA (Minimum)     Large text (≥ 18pt or ≥ 14pt bold)               3:1                                 Headlines, large UI text

    AA (Minimum)          UI components, graphics                     3:1                     Button borders, icons, data visualization markers

   AAA (Enhanced)               Normal text                           7:1               Highest accessibility; required for some compliance standards

   AAA (Enhanced)                Large text                          4.5:1                              Large text enhanced standard
  ---------------- -------------------------------------- ---------------------------- ---------------------------------------------------------------

**A.3 Recommended Data Sources for Training**

  ------------------------------------- ----------------------------------------------------------------------------------- ----------------------------------------------- ------------------------------------------------------------------------------------
          **Dataset / Source**                                              **Content**                                                        **Size**                                                         **Best For**

      Adobe Kuler / Color CC themes          Community-created 5-swatch themes; ratings, tags, user engagement metrics                    Millions of themes                   Harmony learning; popularity/compatibility scores; tag-based semantic learning

              COLOURlovers                               User palettes with names, tags, and pattern usage                               \~3 million palettes                            Semantic tag learning; naming; cultural color associations

    Bahng et al. Text2Colors dataset                       Color palette + descriptive text associations                       Large --- from web scraping + annotation                Text-to-palette; semantic alignment between language and color

   Jonauskaite et al. 2020 (published)       30-country color-emotion association data; open access supplementary data       \~4,500 participants; 12 emotions × 20 colors              Cross-cultural semantic calibration; locale-specific priors

           ColorBrewer schemes           Carefully designed sequential/diverging/qualitative maps; manually expert-created               \~35 curated palettes               Ground-truth training examples for data viz palettes; perceptual quality reference

          Custom human ratings                     Domain-specific labeled palette evaluations from target users                             User-defined                                    Domain-specific fine-tuning; A/B test calibration
  ------------------------------------- ----------------------------------------------------------------------------------- ----------------------------------------------- ------------------------------------------------------------------------------------

**A.4 Key Conversion Formulas**

OkLCH to Oklab: a = C × cos(h°), b = C × sin(h°)

WCAG Relative Luminance: L = 0.2126 × R_lin + 0.7152 × G_lin + 0.0722 × B_lin (where R_lin = R/255 if ≤ 0.04045 else ((R/255 + 0.055)/1.055)\^2.4)

WCAG Contrast Ratio: CR = (L_lighter + 0.05) / (L_darker + 0.05)

Oklab from XYZ: Uses a specific 3×3 matrix transform followed by a cube-root non-linearity. Use an established library (e.g., culori.js, chroma.js, or Python colorspacious) rather than implementing manually.

**APPENDIX B: GLOSSARY**

  ----------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
               **Term**                                                                                                                                             **Definition**

              Achromatic                                                                                                          Having zero chroma (saturation); pure gray, white, or black --- no perceivable hue

              Anisotropy                                                               A shape score derived from PCA eigenvalues: (lambda_1 - lambda_3) / lambda_1. Near 1 = strong directional structure (needle or sheet). Near 0 = spherical cloud palette.

          Centroid (palette)                                                                  The weighted mean position of a palette\'s swatches in OkLCH-Cartesian 3D space. Encodes overall lightness, chroma intensity, and dominant hue direction.

              Chroma (C)                                                                The vividness or colorfulness of a color in perceptual color spaces (OkLCH, CIECAM02). Not equivalent to saturation in HSL. Encodes distance from the achromatic axis.

         Chromatic Adaptation                                                                      The visual system\'s automatic adjustment to the dominant illuminant, keeping \'white\' perceptually stable across different lighting conditions

         CIEDE2000 (DeltaE00)                                                                The gold-standard perceptual color difference metric from the CIE; accounts for non-uniformities in human color perception across hue, lightness, and chroma

            Clusterability                                                 A graph metric measuring how cleanly a palette separates into neutral and accent clusters. Computed as inter-cluster distance / intra-cluster distance. High clusterability = good UI structure.

         Complementarity Index                                                      A continuous measure of how much visual weight sits in opposing hue directions in a palette. Range \[0, 0.5\]. Near 0 = monochromatic. Near 0.5 = equal-weight complementary.

          Convex Hull Volume                                                           The volume of the smallest convex 3D solid containing all palette swatches in OkLCH-Cartesian space. Primary measure of palette diversity and territory in color space.

     CVD (Color Vision Deficiency)                                                                 Colloquial \'color blindness\'; affects \~8% of males and \~0.5% of females. Deuteranopia and protanopia (red-green confusions) are most common.

       Ecological Valence Theory                                                                   Palmer & Schloss (2010): color preference derives from the average affective valence of objects associated with each color in one\'s experience

       Eigenvalue (palette PCA)                                                      One of three values lambda_1 \>= lambda_2 \>= lambda_3 from PCA on the palette\'s weighted covariance matrix. Their ratios classify the palette as needle, sheet, or cloud.

                 Gamut                                                                  The range of colors reproducible by a particular device or color space. sRGB \< Display P3 \< human vision gamut. All geometric operations must check gamut validity.

                Hue Arc                                               The minimum circular arc in degrees that encloses swatches containing 80% or more of a palette\'s total visual weight. Measures hue diversity from monochromatic (\<40 deg) to full-spectrum (\>270 deg).

            Hue Balance (R)                                                            The magnitude of the weighted resultant vector in the hue-chroma plane. R near 0 = hues balance each other out. R near 1 = strongly dominated by a single hue direction.

             L-C Coupling                                              The Pearson correlation between lightness (z) and chroma (r) across swatches. Positive = brighter colors are more saturated (fresh/pop). Negative = darker colors are more saturated (moody/cinematic).

               Linearity                                                                      A PCA-derived shape score: 1 - lambda_2/lambda_1. Near 1 = needle-like palette varying mainly along one axis. Indicates monochromatic or tonal structures.

              Mach Bands                                                                                  Perceptual illusion where the visual system exaggerates luminance edges in gradients, creating apparent bands at transition rates

                Medoid                                                                      The palette swatch with minimum weighted average distance to all other swatches. The most representative single color --- best stand-in for the whole palette.

      Minimum Spanning Tree (MST)                                                                       A graph connecting all palette swatches with minimum total perceptual distance. MST total length = contrast bandwidth of the palette.

                 OkLCH                                                            A 2020 perceptual color space (Björn Ottosson) using Lightness, Chroma, and Hue Angle, designed for maximum perceptual uniformity; recommended for all palette engine computation

            PAD / VAD Model                                                  Pleasure-Arousal-Dominance / Valence-Arousal-Dominance: a 3D model of emotional experience used to quantify color\'s affective impact. Most empirically grounded semantic model for colors.

           Palette Archetype                                       A named geometric pattern of a palette in 3D space: Needle, Fan, Bipolar, Neutral Spine + Spikes, Helix Gradient, or Cloud. Each archetype has characteristic semantic signatures and transformation operators.

               Planarity                                                                     A PCA-derived shape score: 1 - lambda_3/lambda_2. Near 1 = sheet-like palette varying in two axes. Indicates multi-hue palettes at matched lightness levels.

         Point Cloud (palette)                                            The representation of a palette as a set of 3D points in OkLCH-Cartesian space: p_i = (C\*cos(h\*pi/180), C\*sin(h\*pi/180), L). Enables geometric computation of shape, distance, and structure.

          Semantic Invariant                                                                                              A palette property that must remain constant across a transformation to preserve semantic meaning

         Simultaneous Contrast                                                                         Perceptual phenomenon where a color\'s appearance shifts based on surrounding colors; a neutral gray next to orange looks slightly blue

              Sphericity                                                                       A PCA-derived shape score: lambda_3/lambda_1. Near 1 = volumetric cloud palette with variation in all directions. Near 0 = collapsed to a line or plane.

   SPD (Spectral Power Distribution)                                                                         Physical description of a light source or surface --- how much energy at each wavelength; the ground truth of color science

          Topology (palette)                                                                        The structural relationship between swatches in hue, lightness, and chroma space --- defines harmony category (monochromatic, analogous, etc.)

         Trajectory (gradient)                                                         The path gamma(t) in 3D OkLCH-Cartesian space traced by a gradient from t=0 to t=1. Characterized by path length, curvature, lightness monotonicity, and chroma profile.

                 WCAG                                                                        Web Content Accessibility Guidelines; the international standard for digital accessibility, including contrast ratio requirements for text and UI components

         Weighted Point Cloud                                              A palette represented as 3D points where each point carries a weight w_i reflecting its visual area dominance (background=0.60, accent=0.05, etc.). Required for accurate geometric computation.

          Assignment Service                                                The platform service that maps entities (nodes, edges, UI elements) to color tokens. Solves a constrained optimization problem balancing contrast, semantic alignment, and temporal stability.

              Blend Mode                                            A compositing operation defining how a layer\'s colors combine with the layer beneath. Same OkLCH color in multiply mode reads very differently from normal mode --- must be tracked by the Rendering Service.

         Channel Orchestrator                                                                 The service that decides which data dimensions map to which visual channels (color, size, shape, opacity, motion), preventing color from being overloaded.

          Chroma Compression                                                                   The preferred gamut mapping strategy: reduce C at constant L and h until in-gamut. Preserves hue identity and lightness hierarchy better than clipping.

             Color Kernel                                                       The foundational mathematical service: handles all color space conversions, distance metrics, interpolation, gamut checks, and geometric transforms. All other services depend on it.

           Constraint Repair                                                   Minimal adjustments to a palette to satisfy all hard requirements (WCAG, CVD, gamut) while minimizing semantic drift. Implemented as constrained optimization in the Constraint Service.

            CVD Simulation                                                               Modeling how colors appear to observers with color vision deficiency. Brettel/Vienot matrices in LMS color space simulate deuteranopia, protanopia, and tritanopia.

        Data-to-Pixel Compiler                                          A metaphor for the full platform pipeline: human intent compiled through successive stages (semantic specification to palette synthesis to entity assignment to rendering) down to final pixel values.

     Pairwise Interaction (g term)                                             The semantic contribution of two colors appearing together that is not predictable from either color alone. Formally encoded as g(c_i, c_j). Captures the red+black vs red+white effect.

          Redundancy Encoding                                        Critical semantic dimensions should always be encoded in multiple visual channels simultaneously (e.g., error = red color + hexagonal shape + text label), ensuring accessibility and cognitive robustness.

            Semantic Field                                                      A continuous function f mapping every color in color space to its semantic meaning vector. Integrated over a palette\'s weighted geometry to produce the palette\'s aggregate meaning.

           Semantic Inertia                                  A stability constraint in the Assignment Service for dynamic visualizations: a penalty term that resists frame-to-frame color changes, preventing visual flickering while allowing semantically significant re-assignments.

         Wasserstein Distance                                               Optimal transport distance between two probability distributions over color space. Enables palette barycenters (meaningful blends) and perceptually meaningful palette difference measurement.

            AssignmentSpec                               The canonical output of the Assignment Service. Maps every entity (node, edge, UI element) to a color token, swatch ID, and resolved ColorSpec. Includes stability metadata, per-entity diagnostics, and edge color recommendations.

               ColorSpec                                The atomic, typed unit for a single color value in the platform. Contains: color space identifier, channel values, alpha, output profile, and optional metadata. All services accept and produce ColorSpec --- never raw hex strings.

             ConstraintSet                        A typed collection of hard rules a palette must satisfy: WCAG contrast rules per role pair, CVD policy, gamut targets, locked swatches, minimum separation, and forbidden hue ranges. Passed to all generation, repair, and validation operations.

           Context Collapse            A critical failure mode: predicting color meaning as universal when it is domain-specific. Red means urgency in a finance UI; it may mean excitement in a gaming context. Context collapse is prevented by making ContextSpec a required input to all semantic services.

              ContextSpec                                     The typed schema conditioning all semantic predictions. Contains: medium, background, ambient luminance, task type, audience locale, domain, brand constraints, interaction policy, and rendering pipeline specification.

        Hysteresis (assignment)                    A stability mechanism: a new color assignment is only accepted if its quality exceeds the previous assignment by a minimum margin epsilon. Prevents oscillation between two equally good solutions that would otherwise cause visual flickering.

              MeaningSpec                                The typed output of the Semantic Embedding Service. Contains: embedding vector, model version, VAD affect coordinates, keyword scores with confidence, optional per-swatch explanations, and a context hash for staleness detection.

             Mode Collapse                                        A synthesis failure mode: the generation model always produces the same \'safe\' palette regardless of the stated intent. Prevented by enforcing minimum pairwise embedding distance in the candidate set output.

              PaletteSpec                                                 The core platform object representing a complete palette. Contains: versioned ID, ordered SwatchSpec list, optional adjacency graph, context reference, and cached geometry/semantic descriptors.

            Schema Version                                      A required field on all platform objects. Semantic version string (major.minor.patch) that enables cross-version comparisons to detect stale embeddings, inconsistent constraint evaluations, and API contract breaks.

              SwatchSpec                                                                               A typed color-in-context object: ColorSpec plus role, weight, per-swatch constraints, and provenance. The atomic unit of a PaletteSpec.
  ----------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
