🐟 CATFISH CORP

🚗 CATFISH TRAILS A cidade está cada vez mais conectada. Com o avanço dos veículos autônomos, surge um novo desafio: como garantir que esses veículos encontrem sempre a rota mais eficiente em meio a um trânsito dinâmico?

Congestionamentos, acidentes e mudanças repentinas nas condições das vias exigem que esses veículos sejam capazes de recalcular seus caminhos em tempo real, de forma inteligente e segura.

Pensando nesse cenário, desenvolvemos o Catfish Trails, um sistema que simula o comportamento de veículos autônomos em uma malha viária urbana. O projeto utiliza o algoritmo de Dijkstra para encontrar e atualizar, sempre que necessário, o caminho mais curto entre um ponto de origem e um destino, levando em conta alterações no grafo que representa a malha viária da cidade.


🖼️ Demonstrações

![Rota longa](https://github.com/user-attachments/assets/d9820792-d484-4092-8eeb-670c52812dfc)

![Rota curta](https://github.com/user-attachments/assets/154b8229-bb6a-4dbf-b48d-abf1dc71d5e0)



⚙️ Funcionalidades 

✅ Calcular a rota mais eficiente

✅ Calcular a rota menos eficiente

✅ Identificar alterações no trânsito

✅ Estimar o tempo médio de chegada ao destino

✅ Verificar se as coordenadas estão na região de Maricá


🧪 Tecnologias Utilizadas Linguagem: Python

Bibliotecas:

> networkx==3.4.2

> plotly==6.1.1

> scikit-learn==1.6.1

> osmnx==2.0.3


📦 Instalação

1. Clone o repositório:
git clone https://github.com/seu-usuario/catfish-trails.git cd catfish-trails

2. Instale as dependências:
pip install -r requirements.txt

3. Execute o sistema:
python grafo.py


🧭 Como Usar

1. Execute o sistema:
python grafo.py

2. Insira as coordenadas de origem (latitude e longitude)

3. Insira as coordenadas de destino (latitude e longitude)

4. Informe a velocidade média do veículo (em km/h)
   

![Catfish - TUTO](https://github.com/user-attachments/assets/615255c6-5867-46a2-8b76-b0cf66f95f4c)


O sistema irá calcular a melhor rota disponível com base nas condições da malha viária simulada.


👥 Equipe 

![Equipe](https://github.com/user-attachments/assets/9ced4f1a-73cd-4538-9ddb-692edc01fc7a)
