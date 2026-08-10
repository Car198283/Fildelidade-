# Manual de Uso - Captura, Pontos e Resgate de Premios

Este manual explica como usar a area de captura rapida do Fidelidade Total para cadastrar clientes, lancar pontos e resgatar premios.

## 1. Acessar o Sistema

1. Abra o sistema no navegador:
   - No computador: `http://localhost:3003/login`
   - Na rede/celular: `http://192.168.100.31:3003/login`

2. Entre com o usuario da empresa:
   - Email: `cadufcostajf@gmail.com`
   - Senha: `123456`

3. Depois do login, clique no menu **Captura**.
4. No celular, a tela de captura tem quatro abas:
   - **Clientes**
   - **Pontos**
   - **Premiados**
   - **Aniversarios**

## 2. Cadastro de Cliente na Captura

Use esta opcao quando o cliente ainda nao estiver cadastrado.

1. Acesse **Captura**.
2. Clique na aba **Clientes**.
3. Preencha os dados:
   - **Nome completo**: obrigatorio.
   - **Telefone**: recomendado para localizar o cliente depois.
   - **Email**: opcional.
   - **Data de nascimento**: opcional, usada para relatorios de aniversariantes.
4. Clique em **Cadastrar Cliente**.
5. O sistema salva o cliente.

## 3. Cadastro Pelo Celular do Cliente

Use esta opcao quando quiser que o proprio cliente preencha o cadastro no celular.

1. Acesse **Captura**.
2. Clique na aba **Clientes**.
3. Na area **Cadastro Autonomo**, clique em **Gerar link e QR Code**.
4. Envie o link para o cliente ou peca para ele apontar a camera para o QR Code.
5. O cliente preenche os dados e conclui o cadastro.

Importante: o celular precisa estar na mesma rede Wi-Fi do computador quando o sistema estiver rodando localmente.

## 4. Lancamento de Pontos

Use esta opcao quando o cliente comprar e ganhar pontos.

1. Acesse **Captura**.
2. Clique na aba **Pontos**.
3. Busque o cliente pelo nome ou telefone.
4. Clique no cliente correto na lista.
5. Digite a quantidade de pontos.
6. Preencha a descricao, por exemplo:
   - `Compra`
   - `Compra no balcao`
   - `Pedido 123`
7. Clique em **Confirmar Pontos**.
8. O saldo do cliente sera atualizado automaticamente.

## 5. Resgate de Pontos

Use esta opcao quando o cliente premiado trocar os pontos por um premio.

1. Acesse **Captura**.
2. Clique na aba **Premiados**.
3. Localize o cliente.
4. Clique em **Resgatar e Zerar**.
5. Confirme a operacao.
6. O sistema registra o resgate e zera a pontuacao do cliente.

Atencao: essa acao zera todos os pontos atuais do cliente premiado.

## 6. Ver Aniversariantes Pelo Celular

1. Acesse **Captura**.
2. Clique na aba **Aniversarios**.
3. Veja a lista de clientes aniversariantes do mes.
4. Use o botao **Atualizar** para recarregar a lista.

## 7. Resgate de Premio Pelo Dashboard

Use esta opcao quando o cliente ja aparece como premiado no painel principal.

1. Acesse **Dashboard**.
2. Procure a secao **Clientes Premiados (100%)**.
3. Localize o cliente.
4. Clique em **Resgatar premio**.
5. Confirme a operacao.
6. O sistema registra uma saida de pontos e zera o saldo do cliente premiado.

## 8. Conferencia dos Pontos do Cliente

Para conferir o saldo e historico:

1. Acesse **Clientes**.
2. Busque o cliente pelo nome, telefone ou email.
3. Abra os detalhes do cliente.
4. Confira o saldo de pontos e as movimentacoes.

## 9. Boas Praticas

- Sempre confirme se selecionou o cliente correto antes de lancar ou resgatar pontos.
- Use descricoes claras nas movimentacoes.
- Cadastre telefone sempre que possivel, pois facilita a busca.
- Para resgate de premio, confirme com o cliente antes de finalizar.
- Se a tela nao atualizar, recarregue a pagina e confira novamente o cliente.

## 10. Problemas Comuns

### A Captura nao funciona no celular

1. No computador, inicie o sistema pelo arquivo:

   `run.bat`

2. Confira se foram abertas duas janelas:
   - Backend: `http://localhost:8000`
   - Frontend: `http://IP_DO_COMPUTADOR:3003`

3. No celular, use o endereco com o IP do computador, nao use `localhost`:

   `http://192.168.100.31:3003/login`

4. O celular precisa estar no mesmo Wi-Fi do computador.

5. Se a tela abrir, mas nao carregar clientes ou nao salvar pontos, teste no navegador do celular:

   `http://192.168.100.31:8000/health`

   Deve aparecer uma resposta parecida com:

   `{"status":"healthy"}`

6. Se o `/health` nao abrir no celular:
   - confira se a janela do backend esta aberta;
   - permita o Python/backend no Firewall do Windows;
   - confirme se o IP do computador ainda e o mesmo.

7. Depois de ajustar, feche e abra novamente o sistema pelo `run.bat`.

### O cliente nao aparece na busca

- Verifique se digitou o nome ou telefone corretamente.
- Tente buscar por parte do nome.
- Confirme se o cliente foi cadastrado na empresa correta.

### O link ou QR Code nao abre no celular

- Confirme se o celular esta no mesmo Wi-Fi do computador.
- Use o endereco exibido pelo sistema com o IP da rede.
- Se o Windows Firewall perguntar, permita acesso para rede privada.

### O sistema informa senha incorreta

Use:

- Email: `cadufcostajf@gmail.com`
- Senha: `123456`

### O sistema nao abre

Use a porta de producao:

`http://192.168.100.31:3003/login`
