# =====================================================================
# ATIVIDADE PRÁTICA - Programação Orientada a Objetos (Visão Computacional)
# Objetivo: ler uma imagem com N dados sobre fundo neutro e somar as faces.
# Linguagem: Python 3 | Biblioteca: OpenCV (cv2) + NumPy
#
# Estratégia geral (pipeline):
#   1) Segmentação por COR (HSV): isola os dados roxos do fundo cinza.
#   2) Morfologia: fecha buracos (pontos brancos) e remove ruídos.
#   3) Contornos: cada contorno grande = um dado.
#   4) Para cada dado, detecta os PONTOS BRANCOS (limiar adaptativo/Otsu)
#      e separa pontos colados usando Transformada de Distância.
#   5) Conta os pontos de cada dado e soma tudo.
# =====================================================================

import cv2
import numpy as np
from collections import Counter

# ---------------------------------------------------------------------
# Classe que encapsula todo o processamento (orientação a objetos)
# ---------------------------------------------------------------------
class ContadorDeDados:

    def __init__(self, area_minima_dado=1500):
        # área mínima (em pixels) para um contorno ser considerado "dado"
        self.area_minima_dado = area_minima_dado
        # elemento estruturante usado nas operações morfológicas
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    # -----------------------------------------------------------------
    # ETAPA 1-3: encontra os dados na imagem (segmentação por cor)
    # -----------------------------------------------------------------
    def localizar_dados(self, hsv):
        # O HSV separa a cor (H) do brilho (V): o roxo fica em H ~ 115-165
        # e tem saturação alta, o que o distingue do fundo cinza (S baixa).
        mascara = cv2.inRange(hsv, (115, 90, 60), (165, 255, 255))

        # Fechamento: preenche os "buracos" feitos pelos pontos brancos
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, self.kernel, iterations=3)
        # Abertura: elimina pequenos ruídos isolados
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, self.kernel)

        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
        # descarta contornos pequenos (ruído)
        return [c for c in contornos if cv2.contourArea(c) > self.area_minima_dado], mascara

    # -----------------------------------------------------------------
    # ETAPA 4: conta os pontos brancos para UM limiar específico
    # -----------------------------------------------------------------
    def _contar_para_limiar(self, brilho, mascara_dado, lado, limiar):
        # Dilata um pouco a máscara: pontos encostados na borda do dado
        # ficam "de fora" do contorno roxo e seriam perdidos.
        mascara_larga = cv2.dilate(
            mascara_dado, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))

        # Binariza: só o que é bem branco dentro do dado
        pontos = ((brilho > limiar) & (mascara_larga > 0)).astype(np.uint8) * 255

        # Abertura grande remove reflexos finos (brilho nas laterais do dado)
        pontos = cv2.morphologyEx(
            pontos, cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))

        # Transformada de distância: o centro de cada ponto vira um "pico".
        # Isso separa pontos que estão colados na binarização.
        dist = cv2.distanceTransform(pontos, cv2.DIST_L2, 5)
        k = int(lado * 0.2) | 1
        maximos_locais = cv2.dilate(
            dist, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))

        # Mantém só picos com raio compatível com um ponto de dado
        # (proporcional ao tamanho do dado, entre ~9,5% e 15% do lado).
        picos = ((dist == maximos_locais) &
                 (dist >= 0.095 * lado) & (dist <= 0.15 * lado)).astype(np.uint8)

        # Picos vizinhos (platôs com o mesmo valor) são unidos num só
        kj = int(lado * 0.15) | 1
        picos = cv2.dilate(picos, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kj, kj)))
        n, _, _, centros = cv2.connectedComponentsWithStats(picos)
        return [(int(cx), int(cy)) for cx, cy in centros[1:]]  # [0] = fundo

    # -----------------------------------------------------------------
    # ETAPA 4-5: descobre o valor de UM dado (testa vários limiares e
    # escolhe a contagem mais estável - "votação" - para ser robusto
    # a reflexos e diferenças de iluminação nos dados translúcidos)
    # -----------------------------------------------------------------
    def valor_do_dado(self, brilho, contorno):
        casco = cv2.convexHull(contorno)               # inclui pontos da borda
        lado = np.sqrt(cv2.contourArea(casco))         # tamanho aproximado do dado
        mascara = np.zeros(brilho.shape, np.uint8)
        cv2.drawContours(mascara, [casco], -1, 255, -1)

        # Limiar inicial por Otsu, calculado só dentro do dado
        otsu, _ = cv2.threshold(brilho[mascara > 0].reshape(-1, 1), 0, 255,
                                cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        contagens = []
        for limiar in range(int(otsu), 250, 5):
            centros = self._contar_para_limiar(brilho, mascara, lado, limiar)
            if len(centros) > 0:
                contagens.append(len(centros))

        if not contagens:
            return 0
        # valor que mais se repete entre os limiares testados
        return Counter(contagens).most_common(1)[0][0]

    # -----------------------------------------------------------------
    # Processa uma imagem completa
    # -----------------------------------------------------------------
    def processar(self, caminho, salvar_resultado=None):
        imagem = cv2.imread(caminho)
        if imagem is None:
            raise FileNotFoundError(f"Não foi possível abrir a imagem: {caminho}")

        hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)

        # "Brilho branco": V alto E saturação baixa = branco puro.
        # (diferencia os pontos brancos de partes apenas claras do dado)
        brilho = (hsv[:, :, 2].astype(np.float32) *
                  (1 - hsv[:, :, 1].astype(np.float32) / 255)).astype(np.uint8)

        contornos, _ = self.localizar_dados(hsv)

        resultado = imagem.copy()
        valores = []
        for c in contornos:
            valor = self.valor_do_dado(brilho, c)
            valores.append(valor)
            # desenha o retângulo e o valor sobre cada dado
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(resultado, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(resultado, str(valor), (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        soma = sum(valores)
        cv2.putText(resultado, f"Soma = {soma}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 4)
        if salvar_resultado:
            cv2.imwrite(salvar_resultado, resultado)
        return valores, soma, resultado


# ---------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# Processa UMA imagem por vez. O nome do arquivo pode ser passado como
# argumento (python dados.py img1.jpg) ou digitado quando o programa pedir.
# ---------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    # 1) Descobre qual imagem processar
    if len(sys.argv) > 1:
        nome = sys.argv[1]                      # veio como argumento
    else:
        nome = input("Digite o nome da imagem (ex.: img1.jpg): ").strip()

    contador = ContadorDeDados()

    try:
        valores, soma, resultado = contador.processar(
            nome, salvar_resultado="resultado_" + nome)
    except FileNotFoundError as erro:
        print(erro)
        sys.exit(1)

    # 2) Mostra o resultado no terminal
    print(f"Quantidade de dados encontrados: {len(valores)}")
    print(f"Valor de cada dado: {valores}")
    print(f"SOMA DAS FACES: {soma}")

    # 3) Mostra a imagem com as marcações (pressione uma tecla para fechar)
    cv2.imshow("Resultado", cv2.resize(resultado, None, fx=0.5, fy=0.5))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Exemplos de resultado com as imagens de teste fornecidas:
#   img1.jpg: dados = [1, 4, 6]    -> soma = 11
#   img2.jpg: dados = [4]          -> soma = 4
#   img3.jpg: dados = [6, 2, 3, 4] -> soma = 15
#   img4.jpg: dados = [3, 1, 2, 1] -> soma = 7
