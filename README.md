# Log_de_Eventos-Sistemas_Operacionais

## Passo a passo para rodar o projeto

Este projeto permite visualizar logs do sistema operacional via interface gráfica Python, utilizando um leitor de eventos desenvolvido em C# (.NET).

---

## Pré-requisitos

- **Python 3.8+**
- **pip** (gerenciador de pacotes Python)
- **.NET 9.0 SDK e Runtime**  
  - [Download .NET 9.0](https://dotnet.microsoft.com/download/dotnet/9.0)
- **Git** (opcional, para clonar o repositório)

---

## 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/Log_de_Eventos-Sistemas_Operacionais.git
cd Log_de_Eventos-Sistemas_Operacionais
```

---

## 2. Compile o projeto C# (LogReaderApp)

Abra o terminal na pasta do projeto e execute:

```bash
cd LogReaderApp
dotnet build -c Release
```

---

## 3. Instale as dependências Python

```bash
pip install tk
```

---

## 4. Execute o projeto

### **No Windows:**

```bash
python main.py
```

### **No Linux:**

```bash
python3 main.py
```

---

## Observações importantes

- **No Linux:**  
  Certifique-se de que o comando `dotnet` está disponível no terminal (`dotnet --version`).  
  Se necessário, instale o runtime e SDK (ambos 9.0) conforme a documentação oficial:  
  [https://learn.microsoft.com/dotnet/core/install/linux](https://learn.microsoft.com/dotnet/core/install/linux)

- **Permissões:**  
  Para visualizar logs do sistema, pode ser necessário executar o terminal como administrador (Windows) ou com permissões elevadas (Linux).

- **Caminhos:**  
  O projeto espera que o executável/dll do LogReaderApp esteja em `LogReaderApp/bin/Release/net9.0/`.

---

## Dúvidas ou problemas?

Se encontrar algum erro, verifique:
- Se o .NET 9.0 está instalado corretamente (`dotnet --list-sdks` e `dotnet --list-runtimes`)
- Se o projeto foi compilado sem erros
- Se está executando o Python na raiz do projeto

Em caso de dúvidas, entre em contato com o autor
