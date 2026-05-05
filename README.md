[README.md](https://github.com/user-attachments/files/21710199/README.md)

# Roleta Química

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Kivy-33aa33)](https://kivy.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](#licença)

Jogo de perguntas e respostas com **roda da sorte** para tornar aulas e revisões mais engajantes. Defina tempo por questão, equipes, gire a roda e responda. O placar é atualizado em tempo real e cada sessão fica registrada no **Histórico**, com **exportação TXT/CSV**.

<img width="842" height="425" alt="image" src="https://github.com/user-attachments/assets/c07aa9fa-9598-4dff-b936-4c13ff4a63a5" />
<img width="814" height="407" alt="image" src="https://github.com/user-attachments/assets/ad6a323a-f086-4396-9cea-205a004a19a8" />
<img width="729" height="365" alt="image" src="https://github.com/user-attachments/assets/1f733ccf-cdda-40bb-a054-1b735eec2a26" />
<img width="738" height="373" alt="image" src="https://github.com/user-attachments/assets/d8881d39-4f9e-4243-aa40-f3052567c2b5" />



---

# Sumário
- [Como jogar](#como-jogar)
- [Recursos](#recursos)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Bibliotecas e stack](#bibliotecas-e-stack)
- [Adicionar/editar perguntas](#adicionareditar-perguntas)
- [Licença](#licença)

---

# Como jogar

## 1) Introdução
Abra o app e clique em **Começar** para ir à tela inicial.

## 2) Tela de confgurações
Defina rapidamente as regras da sessão:
- **Nº de equipes**
- **Tempo de resposta:** 1:00 a 5:00 (passos de 30 s)
- **Modo de jogo** (ex.: 1º, 2º, 3º ano ou Coffee Lovers)
- **Predefinições** (opcional): carregam filtros prontos
- Acesse **Histórico**, **Adicionar Perguntas** ou **Listar Perguntas** conforme a necessidade


Clique em **Iniciar Jogo**.

## 3) Filtros iniciais
Sem predefinição, um popup pedirá **Áreas** e **Dificuldades** (selecione pelo menos 1 de cada). Com predefinição, os filtros são carregados automaticamente.

## 4) Tela de jogo – girar a roda
- Clique na roda para **girar** (animação com aceleração/desaceleração).
- Ao parar, a área sorteada é destacada e a pergunta correspondente é aberta.
- **Casas especiais** **+5**/**–5** aplicam bônus/penalidade imediata e pulam a vez.


## 5) Respondendo à pergunta
- Um popup exibe **cronômetro**, enunciado e **4 alternativas**. O botão **Dica** pode estar disponível.
- **Acerto:** toca som e soma pontos conforme a dificuldade *(ex.: Fácil 15, Médio 20, Difícil 30)*.
- **Erro/Tempo zerado:** toca som de erro e passa a vez.
- O **placar** é atualizado; a **equipe da vez** alterna automaticamente.


## 6) Encerrar e salvar
Use **Encerrar Jogo** para finalizar. O app calcula a(s) equipe(s) vencedora(s), registra a sessão e volta para a introdução.

## 7) Histórico e exportação
Acesse **Histórico** na tela inicial para rever as sessões. Clique em **Exportar** para gerar **TXT** e **CSV** contendo filtros, perguntas/respostas, tempo de início/fim e placar final.

---

# Recursos
- **Roda animada** com aceleração/frenagem e realce do setor sorteado
- **Placar por equipes** com atualização automática
- **Cronômetro** por pergunta e **efeitos sonoros** (acerto/erro/tempo)
- **Casas especiais** (+5/–5)
- **Histórico completo** por sessão com **exportação TXT/CSV**
- **Pré-carregamento (loading)** de imagens/áudio/vídeo e bancos JSON
- **Múltiplas telas**: introdução, inicial, jogo, listas/editor, predefinições, histórico

---


---

# Estrutura do projeto

```
/ (raiz)
├─ telas_e_botoes.py        # App principal e roteamento de telas
├─ introducao.py            # Tela/fluxo de introdução
├─ loading_screen.py        # Pré-carregamento de assets e dados
├─ preloader.py             # Utilitários de preload
├─ roda_animada.py          # Lógica/anim. da roda
├─ predefinicoes.py         # CRUD de predefinições (filtros prontos)
├─ historico.py             # Visualização e exportação (TXT/CSV)
├─ assets/                  # Imagens, ícones, fundos
├─ sons/                    # Efeitos sonoros
├─ configs/
│  ├─ historico_log.jsonl   # Log das sessões (gravado automaticamente)
│  └─ exports/              # TXT/CSV exportados pelo usuário
└─ dataperguntas/           # Bancos de perguntas (.json)
```

---

# Bibliotecas e stack
- **Linguagem:** Python
- **UI/Animações:** [Kivy](https://kivy.org)
- **Áudio/Vídeo:** [ffpyplayer](https://github.com/matham/ffpyplayer)
- **Dados/Exportação:** `json`, `csv` (stdlib)
- **Utilitários:** `uuid`, `glob`, `random`, `time`, `datetime` (stdlib)

---

# Licença
Distribuído sob a **MIT License**. Veja [LICENSE](https://github.com/devilsir/Quimica-com-cafe/blob/main/LICENSE).
