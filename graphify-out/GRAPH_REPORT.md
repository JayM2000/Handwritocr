# Graph Report - C:\Users\misal\OneDrive\Documents\handwritocr  (2026-06-07)

## Corpus Check
- 61 files · ~39,899 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 350 nodes · 541 edges · 55 communities detected
- Extraction: 64% EXTRACTED · 36% INFERRED · 0% AMBIGUOUS · INFERRED: 194 edges (avg confidence: 0.62)
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

## God Nodes (most connected - your core abstractions)
1. `HandwritingModel` - 31 edges
2. `StyleProfile` - 22 edges
3. `StrokeRenderer` - 20 edges
4. `IAMDataset` - 17 edges
5. `HandwritingGenerator` - 16 edges
6. `run_generation_sync()` - 16 edges
7. `SyntheticStrokeDataset` - 15 edges
8. `MDNParams` - 12 edges
9. `HandwritingTrainer` - 11 edges
10. `GlyphRenderer` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Generate handwriting strokes for given text.          Args:             text: In` --uses--> `HandwritingModel`  [INFERRED]
  C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\ml\inference.py → C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\ml\model.py
- `_run_sync()` --calls--> `run_generation_sync()`  [INFERRED]
  C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\api\endpoints\generate.py → C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\tasks\generation_task.py
- `generate_handwriting()` --calls--> `get_session_sample_paths()`  [INFERRED]
  C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\api\endpoints\generate.py → C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\storage\file_storage.py
- `get_task_status()` --calls--> `get_task_output_dir()`  [INFERRED]
  C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\api\endpoints\generate.py → C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\storage\file_storage.py
- `Health check endpoint.` --uses--> `HealthResponse`  [INFERRED]
  C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\api\endpoints\health.py → C:\Users\misal\OneDrive\Documents\handwritocr\backend\app\models\schemas.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (39): generate_handwriting_task(), Celery task for handwriting generation.  Orchestrates the full pipeline:   1. Ex, Celery task wrapper for handwriting generation., Store task progress in Redis for WebSocket to read., Run the full generation pipeline synchronously.      This is used both by the Ce, run_generation_sync(), _update_progress(), _get_fallback_font() (+31 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (33): Dataset, create_dataloader(), IAMDataset, IAM On-Line Handwriting Dataset loader.  Handles loading and preprocessing of th, Scan the data directory and pair stroke XMLs with transcriptions., Generates synthetic stroke data for testing the model pipeline.      Creates sim, Create a DataLoader with appropriate settings., PyTorch dataset for IAM On-Line Handwriting Database.      Expected directory st (+25 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (33): BaseModel, Enum, generate_task_id(), Generate a unique task ID., generate_handwriting(), get_task_status(), Generate handwriting endpoint., Try to dispatch generation to Celery. Returns False if Celery unavailable. (+25 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (23): parse_iam_stroke_xml(), Return a dummy sample for error cases., Parse an IAM Online stroke XML file.      Returns list of strokes, each a numpy, Convert absolute stroke points to offset format (dx, dy, pen_up).      Args:, raw_strokes_to_offsets(), Stroke-to-image renderer.  Converts stroke sequences (dx, dy, pen_up) to PIL Ima, denormalize_strokes(), indices_to_text() (+15 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (23): download_file(), Download generated files endpoint., Download the generated handwriting file.      Args:         task_id: The generat, cleanup_session(), cleanup_task(), create_session(), create_task_output_dir(), get_output_file() (+15 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (16): generate(), get_inference_engine(), HandwritingInference, Inference engine for handwriting generation.  Takes input text and generates str, Sample a point from the MDN output.          Args:             params: MDN param, Check if model has loaded weights (not random)., Get or create a cached inference engine.      Reuses the same model instance for, Generate handwriting strokes from text using a trained model. (+8 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (20): compute_slant_angle(), compute_stroke_width(), correct_skew(), cv2_to_pil(), load_and_preprocess(), pil_to_cv2(), Low-level image processing utilities using OpenCV and Pillow.  All heavy image o, Extract individual characters from a text line using connected components. (+12 more)

### Community 7 - "Community 7"
Cohesion: 0.17
Nodes (11): Tests for the health endpoint., Root endpoint returns app info., Health endpoint returns ok status., Upload with no files returns 400., Generate with invalid session returns 404., Download nonexistent task returns 404., test_download_nonexistent(), test_generate_invalid_session() (+3 more)

### Community 8 - "Community 8"
Cohesion: 0.22
Nodes (6): MDNLayer, Mixture Density Network head.      Outputs parameters for a mixture of bivariate, Compute MDN parameters from LSTM output.          Args:             x: Combined, Soft attention window over the character sequence.      Uses K Gaussian attentio, Compute attention window.          Args:             lstm_out: Output from first, WindowLayer

### Community 9 - "Community 9"
Cohesion: 0.2
Nodes (4): BaseSettings, Application settings loaded from environment variables., Configuration for the HandwritOCR backend., Settings

### Community 10 - "Community 10"
Cohesion: 0.25
Nodes (7): _draw_blank_paper(), _draw_grid_paper(), _draw_lined_paper(), Server-side PDF generation with notebook-style paper templates.  Uses ReportLab, Draw lined notebook paper with a red margin line., Draw grid/graph paper., Draw blank white paper.

### Community 11 - "Community 11"
Cohesion: 0.33
Nodes (3): HandwritOCR FastAPI Application.  Main entry point for the backend server., Ensure storage directories exist on startup., startup_event()

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (0): 

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (0): 

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (0): 

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): Main API router — aggregates all endpoint routers.

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): Celery application configuration.

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (0): 

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (0): 

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
Nodes (1): Parse comma-separated CORS origins.

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Resolved storage directory path.

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Directory for uploaded samples.

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): Directory for generated outputs.

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (0): 

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
Nodes (0): 

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

## Knowledge Gaps
- **89 isolated node(s):** `Application settings loaded from environment variables.`, `Configuration for the HandwritOCR backend.`, `Parse comma-separated CORS origins.`, `Resolved storage directory path.`, `Directory for uploaded samples.` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 12`** (2 nodes): `layout.tsx`, `RootLayout()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (2 nodes): `page.tsx`, `Home()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (2 nodes): `page.tsx`, `StepSkeleton()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (2 nodes): `router.py`, `Main API router — aggregates all endpoint routers.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (2 nodes): `celery_app.py`, `Celery application configuration.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (2 nodes): `sample-uploader.tsx`, `resizeImage()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (2 nodes): `footer.tsx`, `FooterInner()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `cn()`, `button.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (2 nodes): `glass-card.tsx`, `GlassCardInner()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (2 nodes): `input.tsx`, `Input()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (2 nodes): `utils.ts`, `cn()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (2 nodes): `provider.tsx`, `StoreProvider()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (2 nodes): `generationSlice.ts`, `pollForCompletion()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `eslint.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `next-env.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `next.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `postcss.config.mjs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `Parse comma-separated CORS origins.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Resolved storage directory path.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Directory for uploaded samples.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Directory for generated outputs.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `download-panel.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `drawing-canvas.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `preview-panel.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `text-input.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `navbar.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `animated-background.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `glass-button.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `step-indicator.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `hooks.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `index.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `samplesSlice.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `textSlice.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `uiSlice.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_generation_sync()` connect `Community 0` to `Community 2`, `Community 4`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Why does `HandwritingModel` connect `Community 1` to `Community 8`, `Community 5`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `get_inference_engine()` connect `Community 5` to `Community 0`, `Community 2`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `HandwritingModel` (e.g. with `FineTuner` and `User-specific fine-tuning of the handwriting model.  Takes a pre-trained model a`) actually correct?**
  _`HandwritingModel` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `StyleProfile` (e.g. with `GlyphRenderer` and `HandwritingGenerator`) actually correct?**
  _`StyleProfile` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `StrokeRenderer` (e.g. with `GlyphRenderer` and `HandwritingGenerator`) actually correct?**
  _`StrokeRenderer` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `IAMDataset` (e.g. with `HandwritingTrainer` and `Training pipeline for the handwriting synthesis model.  Provides:   - Handwritin`) actually correct?**
  _`IAMDataset` has 9 INFERRED edges - model-reasoned connections that need verification._