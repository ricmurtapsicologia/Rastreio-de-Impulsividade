from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')
original = s

questions_before = re.findall(r'<div class="question">.*?</div>', s, re.S)
assert len(questions_before) == 30, f'expected 30 question blocks, got {len(questions_before)}'

replacements = {
    '<title>Rastreio de Impulsividade </title>': '<title>Decisão, planejamento e controle de impulsos</title>',
    '<meta property="og:title" content="Rastreio de Impulsividade" />': '<meta property="og:title" content="Decisão, planejamento e controle de impulsos" />',
    '<meta property="og:description" content="Avalie sua impulsividade com esta escala detalhada." />': '<meta property="og:description" content="Rastreio clínico sobre padrões de decisão, planejamento e resposta no dia a dia." />',
    '<h1 style="color: white; font-size: 48px; font-weight: bold; text-align: center; margin: 0; padding: 20px 0;">Rastreio de Impulsividade</h1>': '<h1 style="color: white; font-size: 48px; font-weight: bold; text-align: center; margin: 0; padding: 20px 0;">Decisão, planejamento e controle de impulsos</h1>',
    '<p>Esta escala foi desenvolvida para medir a impulsividade. Responda cada questão conforme você realmente se sente, utilizando a seguinte escala para cada afirmação:</p>': '<p>Este rastreio observa padrões de decisão, planejamento e resposta no dia a dia. Responda cada questão com base na sua experiência real.</p>',
    '<button type="button" onclick="calculateScore()">Calcular</button>': '<button type="button" id="btnConcluir">Concluir rastreio</button>',
}
for old, new in replacements.items():
    if old in s:
        s = s.replace(old, new, 1)

# Remove gauge dependencies; no patient scoring is allowed while scorer is blocked.
s = re.sub(r'\n?\s*<link rel="stylesheet" href="https://cdnjs\.cloudflare\.com/ajax/libs/justgage/[^>]+>', '', s)
s = re.sub(r'\n?\s*<script src="https://cdnjs\.cloudflare\.com/ajax/libs/raphael/[^>]+></script>', '', s)
s = re.sub(r'\n?\s*<script src="https://cdnjs\.cloudflare\.com/ajax/libs/justgage/[^>]+></script>', '', s)

# Remove result-only CSS blocks.
s = re.sub(r'\n\s*\.gauge-container\s*\{.*?\n\s*\}', '', s, flags=re.S)
s = re.sub(r'\n\s*\.gauge-desc\s*\{.*?\n\s*\}', '', s, flags=re.S)
s = re.sub(r'\n\s*\.result-section\s*\{.*?\n\s*\}', '', s, flags=re.S)
s = re.sub(r'\n\s*\.result-item\s*\{.*?\n\s*\}', '', s, flags=re.S)

# Remove gauge/result markup but preserve all question blocks and response options.
s = re.sub(r'\n\s*<div class="gauge-container">.*?</div>\s*</div>', '', s, count=1, flags=re.S)
s = re.sub(r'\n\s*<div class="result-section" id="results"></div>', '', s, count=1)

# Remove the complete legacy scoring/percentile runtime.
s, n = re.subn(r'\n\s*<script>\s*let impulsivityGauge;.*?</script>', '', s, count=1, flags=re.S)
assert n == 1, 'legacy impulsivity scorer script not found exactly once'

questions_after = re.findall(r'<div class="question">.*?</div>', s, re.S)
assert questions_after == questions_before, 'question wording/options changed during sanitization'

for token in (
    'calculateScore()',
    'displayResults(',
    'determinePercentile(',
    'interpretPercentile(',
    'Função simulada para determinar o percentil',
    'Percentil:',
    'JustGage',
    'impulsivityGauge',
    'id="results"',
):
    assert token not in s, f'legacy patient-result token remains: {token}'

assert 'Concluir rastreio' in s
assert 'screening-uniformity-v1.js' in s
assert s != original
p.write_text(s, encoding='utf-8')
