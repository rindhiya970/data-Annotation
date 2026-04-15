-- Migration: Add image annotation support
-- Description: Extend annotations table to support both image and video frame annotations

-- Step 1: Make video_id and frame_id nullable
ALTER TABLE annotations 
    MODIFY COLUMN video_id INT NULL,
    MODIFY COLUMN frame_id INT NULL;

-- Step 2: Add file_id column for image annotations
ALTER TABLE annotations 
    ADD COLUMN file_id INT NULL AFTER user_id,
    ADD CONSTRAINT fk_annotations_file 
        FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE;

-- Step 3: Add check constraint to ensure either file_id OR frame_id is set (not both, not neither)
ALTER TABLE annotations 
    ADD CONSTRAINT chk_annotation_target 
        CHECK (
            (file_id IS NOT NULL AND frame_id IS NULL AND video_id IS NULL) OR
            (file_id IS NULL AND frame_id IS NOT NULL AND video_id IS NOT NULL)
        );

-- Step 4: Add index for file_id lookups
CREATE INDEX idx_annotations_file_id ON annotations(file_id);

-- Rollback script (if needed):
-- ALTER TABLE annotations DROP CONSTRAINT chk_annotation_target;
-- ALTER TABLE annotations DROP FOREIGN KEY fk_annotations_file;
-- ALTER TABLE annotations DROP COLUMN file_id;
-- ALTER TABLE annotations MODIFY COLUMN video_id INT NOT NULL;
-- ALTER TABLE annotations MODIFY COLUMN frame_id INT NOT NULL;
-- DROP INDEX idx_annotations_file_id ON annotations;
