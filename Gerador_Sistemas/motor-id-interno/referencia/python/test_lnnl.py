"""Testes da implementação de referência LNNL.  Rodar:  python -m unittest test_lnnl.py"""
import json
import random
import unittest
from itertools import combinations
from pathlib import Path

import lnnl

VETORES = json.loads((Path(__file__).resolve().parents[2] / 'vetores-teste.json').read_text(encoding='utf-8'))


class VetoresTests(unittest.TestCase):
    def test_constantes_normativas(self):
        self.assertEqual(list(lnnl.PESOS), VETORES['pesos'])
        self.assertEqual(lnnl.MODULO, VETORES['modulo'])
        self.assertEqual(lnnl.TIPO_RESERVADO, VETORES['tipo_reservado'])

    def test_validos(self):
        for v in VETORES['validos']:
            with self.subTest(dados=v['dados_12']):
                self.assertEqual(lnnl.montar(v['dados_12']), v['canonico'])
                self.assertEqual(lnnl.formatar(v['canonico']), v['formatado'])
                self.assertTrue(lnnl.validar(v['formatado']))

    def test_invalidos_com_codigo_de_erro(self):
        for v in VETORES['invalidos']:
            with self.subTest(entrada=v['entrada']):
                self.assertEqual(lnnl.validar(v['entrada']).erro, v['erro'])

    def test_normalizacao_e_tipo_esperado(self):
        for v in VETORES['normalizacao']:
            self.assertEqual(lnnl.validar(v['entrada']).canonico, v['canonico'])
        for v in VETORES['tipo_esperado']:
            self.assertEqual(lnnl.validar(v['entrada'], v['tipo_esperado']).erro, v['erro'])


class GarantiasMatematicasTests(unittest.TestCase):
    def test_pesos_distintos_e_nao_nulos_mod_79(self):
        residuos = [p % lnnl.MODULO for p in lnnl.PESOS]
        self.assertNotIn(0, residuos)
        self.assertEqual(len(set(residuos)), 12)
        # Transposição verificador ↔ dígito de dados só escaparia com peso ≡ 70 ou 78 (Apêndice A.3b).
        self.assertFalse({70, 78} & set(residuos))

    def test_toda_troca_de_um_caractere_e_detectada_exaustivo(self):
        base = 'K12WF22MT5RQ7L'
        for i, classe in enumerate(lnnl.CLASSES):
            for ch in lnnl.LETRAS + lnnl.DIGITOS + '0':
                if ch == base[i]:
                    continue
                with self.subTest(posicao=i + 1, caractere=ch):
                    self.assertFalse(lnnl.validar(base[:i] + ch + base[i + 1:]))

    def test_toda_transposicao_e_detectada_exaustivo(self):
        rng = random.Random(1)
        for _ in range(200):
            s = lnnl.gerar(rng.choice(lnnl.codigos_tipo_disponiveis()), aleatorio=rng)
            for i, j in combinations(range(14), 2):
                if s[i] == s[j]:
                    continue
                t = list(s)
                t[i], t[j] = t[j], t[i]
                self.assertFalse(lnnl.validar(''.join(t)), (s, i, j))


class GeracaoTests(unittest.TestCase):
    def test_gera_validos_do_tipo_pedido(self):
        for tipo in ('11', '14', 99, '62'):
            ident = lnnl.gerar(tipo)
            self.assertTrue(lnnl.validar(ident, tipo))
            self.assertEqual(lnnl.extrair_tipo(ident), f'{int(tipo):02d}')

    def test_recusa_tipo_reservado_e_tipos_com_zero(self):
        for tipo in ('93', '10', '05', '100', 'AB'):
            with self.subTest(tipo=tipo), self.assertRaises(ValueError):
                lnnl.gerar(tipo)

    def test_80_tipos_atribuiveis(self):
        tipos = lnnl.codigos_tipo_disponiveis()
        self.assertEqual(len(tipos), 80)
        self.assertNotIn('93', tipos)

    def test_candidatos_de_correcao_incluem_o_original(self):
        original = 'K12WF22MT5RQ7L'
        candidatos = lnnl.candidatos_correcao('K12WF22MT5RQ7M')
        self.assertIn(original, candidatos)
        self.assertTrue(all(lnnl.validar(c) for c in candidatos))


if __name__ == '__main__':
    unittest.main()
