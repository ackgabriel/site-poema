# site-poema

Galeria de poemas feita com [Streamlit](https://streamlit.io). Cada poema é um
arquivo de texto na pasta `poemas/` — publicar um poema novo é criar um arquivo
e dar `git push`.

## Como adicionar um poema

Crie `poemas/qualquer-nome.md` com este formato:

```markdown
---
titulo: Maré
data: 2026-01-12
tags: [mar, tempo]
epigrafe: uma linha em itálico antes do poema (opcional)
nota: comentário que aparece no rodapé do poema (opcional)
---
A água chega sem pressa
e leva o que a areia guardava:
uma pegada, um bilhete.
```

Só `titulo` e o corpo são obrigatórios.

## Fotos dentro do poema

Ponha o arquivo de imagem em `fotos/` e escreva, numa linha sozinha, no ponto
exato do poema onde ela deve aparecer:

```
[foto: proa.jpg]
[foto: proa.jpg | legenda opcional]
```

Use `.jpg`, `.png` ou `.webp` — HEIC (o formato do iPhone) não abre no
navegador. Vale redimensionar para no máximo ~1800px antes de subir, para o
site carregar rápido; converter também descarta os metadados da foto,
inclusive a localização de GPS que o celular grava.
 As quebras de linha e os espaços são
preservados exatamente como você escrever — o site não reformata verso.

Os poemas aparecem do mais recente para o mais antigo, pela `data`.

## Rodar no seu computador

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre em <http://localhost:8501>.

## Publicar de graça no Streamlit Community Cloud

1. Suba este repositório para o GitHub (pode ser público ou privado).
2. Entre em <https://share.streamlit.io> com a conta do GitHub.
3. **Create app** → escolha o repositório, branch `main`, arquivo `app.py`.
4. **Deploy**. Em um ou dois minutos o site fica no ar em
   `https://SEU-APP.streamlit.app`.

Depois disso, todo `git push` na branch `main` atualiza o site sozinho.

## Estrutura

```
app.py                 o site inteiro
poemas/                um arquivo .md por poema
requirements.txt       dependências
.streamlit/config.toml tema (cores e fontes)
```

## Ajustes rápidos

No topo do `app.py`:

- `TITULO_DO_SITE` — o nome que aparece na barra lateral
- `AUTOR` — a assinatura logo abaixo

As cores e as fontes ficam no bloco `CSS`, também no `app.py` (papel, tinta e
fio; há uma versão para modo escuro no fim do bloco).

Links diretos para um poema funcionam: `?poema=mare` abre aquele poema.
