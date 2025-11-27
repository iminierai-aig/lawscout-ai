import json
from pathlib import Path

print('\n✅ Verification:\n')
total = 0
for f in Path('data/embeddings').glob('*.json'):
    with open(f) as file:
        data = json.load(file)
    chunks = len(data)
    total += chunks
    size = f.stat().st_size / (1024**2)
    
    has_embedding = 'embedding' in data[0] if data else False
    
    print(f'{f.name}:')
    print(f'  Chunks: {chunks:,}')
    print(f'  Size: {size:.1f} MB')
    print(f'  Has embeddings:', '✅' if has_embedding else '❌')
    if has_embedding:
        print(f'  Embedding dims: {len(data[0]["embedding"])}')
    print()

print(f'Total: {total:,} vectors')
print(f'Expected: 171,813 vectors')
print('Match:', '✅ YES' if total == 171813 else '⚠️ NO')
