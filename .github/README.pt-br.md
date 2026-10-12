# AIOS Second Brain

Um segundo cérebro que uma IA consegue operar. Um vault do Obsidian com regras, memória, skills e verificações já ligadas ao Claude Code: toda sessão começa sabendo quem você é, o que aconteceu da última vez e onde cada coisa vai.

Gratuito e de código aberto. [English](../README.md)

> Projeto independente. Sem vínculo com a Obsidian nem com a Anthropic.

O vault fala inglês por dentro (regras, skills e mensagens). A IA responde no idioma em que você escrever.

## Começar em um minuto

Não precisa saber git nem terminal.

1. Instale o [Claude Code](https://claude.com/code) (plano Pro ou Max), o [Obsidian](https://obsidian.md/download), o [Git](https://git-scm.com) e o [Python 3](https://www.python.org/downloads/).
2. Crie uma pasta vazia para o seu segundo cérebro, por exemplo `segundo-cerebro` dentro de Documentos. **Fora de Downloads e da Área de Trabalho, e sem espaço no nome da pasta.**
3. Abra o Claude Code **dentro dessa pasta**.
4. Cole esta frase:

```
Criar meu segundo cérebro com este repositório: https://github.com/rodolfoburque/aios-second-brain
```

5. Aceite as permissões. Não digite nenhum comando com `/`. O Claude faz a instalação e te pergunta algumas coisas sobre você.

A frase precisa do link. "Criar meu segundo cérebro" sozinho não basta.

As instruções que a IA segue estão no [README em inglês](../README.md), no bloco "If you are the AI".

## O que vem

- **Memória entre sessões:** um hook entrega sua identidade e a última sessão a cada conversa nova, e escreve a nota do dia quando a sessão termina.
- **Cada coisa no lugar:** "processa isso pro vault" com um link, arquivo ou texto. Ele lê, destila e guarda a nota na pasta certa, ligada ao que já existe.
- **Verificação:** scripts conferem links, frontmatter, nota órfã e as próprias skills.
- **Trava de segredo:** um hook barra commit com senha ou token.

São 5 comandos, 10 skills, 5 agentes e os hooks. A lista completa fica em `AIOS/index.md` depois de instalar.

## Requisitos

Claude Code, Obsidian, Git e Python 3. Provado no Windows 11. No macOS e no Linux vale o arquivo de configuração padrão; se algo falhar, abra uma issue com a saída do `test-hooks.py`.

## Veja o seu vault se mexer

O [vaultbubbles.org/br](https://vaultbubbles.org/br) lê uma pasta de notas no navegador e mostra em bolhas o que você anda trabalhando. Nada sai da sua máquina.

## Próximos passos

- **AIOS Tools e AIOS Skills:** packs que rodam em cima deste vault. [vaultbubbles.org/br/aios-tools](https://vaultbubbles.org/br/aios-tools)
- **Quer isso instalado na operação da sua empresa?** [bvrx.studio](https://bvrx.studio)

## Licença

MIT. Ver [LICENSE](../LICENSE).
