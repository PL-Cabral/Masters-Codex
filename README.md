# Master's Codex

**Master's Codex** é uma aplicação de terminal desenvolvida em Python para auxiliar tanto Dungeon Masters (Mestres) quanto Jogadores no gerenciamento de campanhas de RPG de mesa. 

O sistema substitui as antigas fichas de papel e rolagens manuais por uma plataforma centralizada e orientada a objetos, onde dados, atributos, habilidades e inventários são sincronizados em nuvem através do Firebase. 

Projeto desenvolvido como requisito avaliativo da disciplina de Linguagem de Programação.

---

## Funcionalidades Principais

* **Acesso Multiusuário:** O sistema foi projetado para integrar a mesa inteira. Jogadores gerenciam seus próprios heróis, enquanto o Mestre controla NPCs, Monstros e o fluxo da sessão.
* **Rolagem de Dados Automatizada (Engine):** Motor de física simulado para rolagens (D4, D6, D10, D20, D100) com ordenação cronológica e cálculo automático de modificadores de atributos (ex: Força, Destreza).
* **Gerenciamento de Entidades (CRUD):** Criação, leitura, atualização e remoção de atributos, condições de combate e itens de inventário.
* **Sincronização em Nuvem:** Persistência de dados utilizando o Firebase Realtime Database. O estado do jogo é salvo e carregado automaticamente ao iniciar.

---

## Arquitetura e Padrões de Projeto (POO)

Para atender aos critérios acadêmicos e garantir a manutenibilidade do código, o sistema foi construído da seguinte forma:

* **Herança e Abstração:** Utilização de uma classe base abstrata `Entity` da qual derivam classes com comportamentos específicos e não-vazios (`Player`, `Monster`, `NPC`).
* **Polimorfismo:** O método `perform_action()` é sobrescrito. Enquanto um `Player` calcula modificadores de D&D baseados em raça/classe ao agir, um `NPC` possui um retorno narrativo baseado em seu comportamento (amigável/hostil).
* **Regras de Negócio e Validações:** O sistema impede status impossíveis (como HP negativo ou níveis zerados) e bloqueia ações de entidades mortas (`current_hp == 0`).
* **Tratamento de Exceções Customizadas:** Erros de domínio foram isolados na camada `utility/exceptions.py` (ex: `AttributeValidationError`, `EntityCannotActError`).
* **Máquina de Estados Dinâmica:** A sessão gerencia regras rígidas de transição de fase (Preparação -> Exploração <-> Combate -> Encerrada).

---

## Estrutura de Diretórios


```text
Masters-Codex/
│
├── core/                # Regras de negócio e classes do domínio (Entity, Player, Monster, NPC)
├── engine/              # Lógica de motor do jogo (Rolagem de dados, Máquina de Estados)
├── services/            # Integração com APIs externas (FirebaseCRUD)
├── utility/             # Ferramentas de apoio e Exceções customizadas
├── secrets/             # Chaves privadas (ignorado no .gitignore)
├── main.py              # Ponto de entrada e interface de terminal (Menu)
└── README.md            # Documentação do projeto
