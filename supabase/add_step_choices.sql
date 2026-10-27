-- SupabaseのSQL Editorで実行してください。
-- 実テーブルに不足していた自己分析Aの3列だけを追加します。
-- 既存の行や、それ以外の列は変更しません。
ALTER TABLE public.company_research
    ADD COLUMN IF NOT EXISTS step1_choices text[],
    ADD COLUMN IF NOT EXISTS step2_choices text[],
    ADD COLUMN IF NOT EXISTS step3_choices text[];
