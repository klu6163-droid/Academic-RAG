param(
    [switch]$KeepEmbeddingCache
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$EmbeddingCache = Join-Path $ProjectRoot "data\cache\embeddings\evidence_embeddings.npy"
$FaissIndex = Join-Path $ProjectRoot "data\cache\faiss_index\evidence.index"

if (-not $KeepEmbeddingCache -and (Test-Path $EmbeddingCache)) {
    Remove-Item -LiteralPath $EmbeddingCache -Force
    Write-Host "Removed embedding cache: $EmbeddingCache"
}

if (Test-Path $FaissIndex) {
    Remove-Item -LiteralPath $FaissIndex -Force
    Write-Host "Removed FAISS index: $FaissIndex"
}

Push-Location $ProjectRoot
try {
    python -B -c "from src.rag.service import get_service; stats=get_service().get_stats(); print({k: stats[k] for k in ['evidence_rows','unique_papers','faiss_vectors','bm25_ready','retriever']})"
} finally {
    Pop-Location
}
