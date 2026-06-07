# Graph Report - C:\Users\misal\OneDrive\Documents\handwritocr  (2026-06-07)

## Corpus Check
- 63 files · ~71,232 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 419 nodes · 655 edges · 65 communities detected
- Extraction: 61% EXTRACTED · 39% INFERRED · 0% AMBIGUOUS · INFERRED: 254 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]

## God Nodes (most connected - your core abstractions)
1. `StyleProfile` - 33 edges
2. `HandwritingModel` - 31 edges
3. `StrokeRenderer` - 31 edges
4. `HandwritingGenerator` - 21 edges
5. `run_generation_sync()` - 20 edges
6. `IAMDataset` - 17 edges
7. `PenProfile` - 16 edges
8. `SyntheticStrokeDataset` - 15 edges
9. `PDFGenerator` - 13 edges
10. `StyleExtractor` - 13 edges

## Surprising Connections (you probably didn't know these)
- `User-specific fine-tuning of the handwriting model.  Takes a pre-trained model a` --uses--> `HandwritingModel`  [INFERRED]
  C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\ml\fine_tune.py → C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\ml\model.py
- `Extract approximate stroke data from a handwriting image.      Uses morphologica` --uses--> `HandwritingModel`  [INFERRED]
  C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\ml\fine_tune.py → C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\ml\model.py
- `Simple skeletonization fallback when cv2.ximgproc is unavailable.` --uses--> `HandwritingModel`  [INFERRED]
  C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\ml\fine_tune.py → C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\ml\model.py
- `Fine-tune a pre-trained model on user's handwriting samples.` --uses--> `HandwritingModel`  [INFERRED]
  C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\ml\fine_tune.py → C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\ml\model.py
- `Fine-tune the model on user's handwriting samples.          Args:             sa` --uses--> `HandwritingModel`  [INFERRED]
  C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\ml\fine_tune.py → C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\ml\model.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (40): Dataset, create_dataloader(), IAMDataset, IAM On-Line Handwriting Dataset loader.  Handles loading and preprocessing of th, Scan the data directory and pair stroke XMLs with transcriptions., Generates synthetic stroke data for testing the model pipeline.      Creates sim, Create a DataLoader with appropriate settings., PyTorch dataset for IAM On-Line Handwriting Database.      Expected directory st (+32 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (44): FineTuner, Fine-tune a pre-trained model on user's handwriting samples., Fine-tune the model on user's handwriting samples.          Args:             sa, generate_handwriting_task(), Celery task for handwriting generation.  Orchestrates the full pipeline:   1. Ex, Celery task wrapper for handwriting generation., Celery task wrapper for handwriting generation., Celery task wrapper for handwriting generation. (+36 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (40): _get_fallback_font(), GlyphRenderer, Handwriting generation engine.  Takes a style profile and input text, then gener, Generate handwriting pages from input text.          Returns list of PIL Images,, Check if an ML model checkpoint is available., Check if an ML model checkpoint is available., Render text using a handwriting font with procedural randomness., Get the ML checkpoint path for this session. (+32 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (36): BaseModel, Enum, get_session_dir(), get_session_sample_paths(), Get the upload directory for a session., List all sample image paths in a session., generate_handwriting(), get_task_status() (+28 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (23): parse_iam_stroke_xml(), Return a dummy sample for error cases., Parse an IAM Online stroke XML file.      Returns list of strokes, each a numpy, Convert absolute stroke points to offset format (dx, dy, pen_up).      Args:, raw_strokes_to_offsets(), Stroke-to-image renderer.  Converts stroke sequences (dx, dy, pen_up) to PIL Ima, denormalize_strokes(), indices_to_text() (+15 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (21): download_file(), Download generated files endpoint., Download the generated handwriting file.      Args:         task_id: The generat, cleanup_session(), cleanup_task(), create_session(), create_task_output_dir(), generate_task_id() (+13 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (13): create_imperfection_engine(), ImperfectionEngine, Natural imperfections engine for handwriting rendering.  Adds realistic human im, Vary opacity to simulate pen pressure changes., Simulate ink bleeding into paper fibres (slight edge feathering)., Add occasional ghost re-strikes (faint shadow offset)., Apply occasional directional smudge blur., Applies natural imperfections to handwriting page images. (+5 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (17): _draw_blank_paper(), _draw_cornell_paper(), _draw_dotted_paper(), _draw_engineering_paper(), _draw_grid_paper(), _draw_lined_paper(), _draw_margin_ruled_paper(), _draw_vintage_paper() (+9 more)

### Community 8 - "Community 8"
Cohesion: 0.17
Nodes (11): Tests for the health endpoint., Root endpoint returns app info., Health endpoint returns ok status., Upload with no files returns 400., Generate with invalid session returns 404., Download nonexistent task returns 404., test_download_nonexistent(), test_generate_invalid_session() (+3 more)

### Community 9 - "Community 9"
Cohesion: 0.22
Nodes (6): MDNLayer, Mixture Density Network head.      Outputs parameters for a mixture of bivariate, Compute MDN parameters from LSTM output.          Args:             x: Combined, Soft attention window over the character sequence.      Uses K Gaussian attentio, Compute attention window.          Args:             lstm_out: Output from first, WindowLayer

### Community 10 - "Community 10"
Cohesion: 0.2
Nodes (4): BaseSettings, Application settings loaded from environment variables., Configuration for the HandwritOCR backend., Settings

### Community 11 - "Community 11"
Cohesion: 0.33
Nodes (3): HandwritOCR FastAPI Application.  Main entry point for the backend server., Ensure storage directories exist on startup., startup_event()

### Community 12 - "Community 12"
Cohesion: 0.4
Nodes (5): extract_strokes_from_image(), User-specific fine-tuning of the handwriting model.  Takes a pre-trained model a, Simple skeletonization fallback when cv2.ximgproc is unavailable., Extract approximate stroke data from a handwriting image.      Uses morphologica, _simple_skeleton()

### Community 13 - "Community 13"
Cohesion: 0.4
Nodes (3): CharacterMetrics, Handwriting style extraction from sample images.  Analyses uploaded handwriting, Metrics for a single extracted character.

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (0): 

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (0): 

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (0): 

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): Main API router — aggregates all endpoint routers.

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): Celery application configuration.

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (0): 

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (0): 

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (0): 

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (0): 

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (0): 

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (0): 

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (0): 

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (0): 

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Parse comma-separated CORS origins.

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): Resolved storage directory path.

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): Directory for uploaded samples.

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): Directory for generated outputs.

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): How consistent the user's writing is (0–1, higher = more consistent).

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (0): 

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (0): 

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (0): 

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (0): 

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (0): 

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (0): 

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (0): 

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (0): 

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (0): 

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (0): 

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (0): 

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (0): 

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Generates notebook-style PDFs from handwriting page images.

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Metrics for a single extracted character.

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Complete handwriting style profile extracted from samples.

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Extracts handwriting style from sample images.

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): Analyse multiple handwriting samples and build a style profile.          Args:

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Request body for POST /api/generate.

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): WebSocket progress message format.

## Knowledge Gaps
- **118 isolated node(s):** `Application settings loaded from environment variables.`, `Configuration for the HandwritOCR backend.`, `Parse comma-separated CORS origins.`, `Resolved storage directory path.`, `Directory for uploaded samples.` (+113 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 14`** (2 nodes): `layout.tsx`, `RootLayout()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (2 nodes): `page.tsx`, `Home()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (2 nodes): `page.tsx`, `StepSkeleton()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (2 nodes): `router.py`, `Main API router — aggregates all endpoint routers.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (2 nodes): `celery_app.py`, `Celery application configuration.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `sample-uploader.tsx`, `resizeImage()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (2 nodes): `footer.tsx`, `FooterInner()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (2 nodes): `cn()`, `button.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (2 nodes): `glass-card.tsx`, `GlassCardInner()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (2 nodes): `input.tsx`, `Input()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (2 nodes): `utils.ts`, `cn()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (2 nodes): `provider.tsx`, `StoreProvider()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (2 nodes): `generationSlice.ts`, `pollForCompletion()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `eslint.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `next-env.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `next.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `postcss.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Parse comma-separated CORS origins.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Resolved storage directory path.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `Directory for uploaded samples.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `Directory for generated outputs.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `How consistent the user's writing is (0–1, higher = more consistent).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `download-panel.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `drawing-canvas.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `preview-panel.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `text-input.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `navbar.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `animated-background.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `glass-button.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `step-indicator.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `hooks.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `index.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `samplesSlice.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `textSlice.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `uiSlice.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `Generates notebook-style PDFs from handwriting page images.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `Metrics for a single extracted character.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `Complete handwriting style profile extracted from samples.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `Extracts handwriting style from sample images.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `Analyse multiple handwriting samples and build a style profile.          Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `Request body for POST /api/generate.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `WebSocket progress message format.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_generation_sync()` connect `Community 1` to `Community 0`, `Community 3`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.220) - this node is a cross-community bridge._
- **Why does `HandwritingModel` connect `Community 0` to `Community 9`, `Community 12`, `Community 1`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `PDFGenerator` connect `Community 1` to `Community 7`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `StyleProfile` (e.g. with `GlyphRenderer` and `HandwritingGenerator`) actually correct?**
  _`StyleProfile` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `HandwritingModel` (e.g. with `FineTuner` and `User-specific fine-tuning of the handwriting model.  Takes a pre-trained model a`) actually correct?**
  _`HandwritingModel` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `StrokeRenderer` (e.g. with `GlyphRenderer` and `HandwritingGenerator`) actually correct?**
  _`StrokeRenderer` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `HandwritingGenerator` (e.g. with `StyleProfile` and `PenProfile`) actually correct?**
  _`HandwritingGenerator` has 12 INFERRED edges - model-reasoned connections that need verification._