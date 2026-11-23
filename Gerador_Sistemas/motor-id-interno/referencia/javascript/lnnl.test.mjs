// Testes da implementação de referência LNNL.  Rodar:  node --test lnnl.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  PESOS, MODULO, TIPO_RESERVADO, CLASSES, LETRAS, DIGITOS,
  montar, formatar, validar, gerar, candidatosCorrecao, extrairTipo,
} from './lnnl.mjs';

const VETORES = JSON.parse(readFileSync(new URL('../../vetores-teste.json', import.meta.url), 'utf8'));

test('constantes normativas iguais às dos vetores', () => {
  assert.deepEqual([...PESOS], VETORES.pesos);
  assert.equal(MODULO, VETORES.modulo);
  assert.equal(TIPO_RESERVADO, VETORES.tipo_reservado);
});

test('vetores válidos', () => {
  for (const v of VETORES.validos) {
    assert.equal(montar(v.dados_12), v.canonico);
    assert.equal(formatar(v.canonico), v.formatado);
    assert.equal(validar(v.formatado).valido, true);
  }
});

test('vetores inválidos com código de erro', () => {
  for (const v of VETORES.invalidos) assert.equal(validar(v.entrada).erro, v.erro, v.entrada);
});

test('normalização e tipo esperado', () => {
  for (const v of VETORES.normalizacao) assert.equal(validar(v.entrada).canonico, v.canonico);
  for (const v of VETORES.tipo_esperado) assert.equal(validar(v.entrada, v.tipo_esperado).erro, v.erro);
});

test('toda troca de um caractere é detectada', () => {
  const base = 'K12WF22MT5RQ7L';
  for (let i = 0; i < 14; i++) {
    for (const ch of LETRAS + DIGITOS + '0') {
      if (ch === base[i]) continue;
      assert.equal(validar(base.slice(0, i) + ch + base.slice(i + 1)).valido, false);
    }
  }
});

test('geração: válidos, tipo preservado, 93 recusado', () => {
  for (let k = 0; k < 500; k++) {
    const id = gerar('14');
    assert.equal(validar(id, '14').valido, true);
    assert.equal(extrairTipo(id), '14');
    assert.equal(id.length, CLASSES.length);
  }
  assert.throws(() => gerar('93'));
  assert.throws(() => gerar('10'));
});

test('candidatos de correção incluem o original', () => {
  assert.ok(candidatosCorrecao('K12WF22MT5RQ7M').includes('K12WF22MT5RQ7L'));
});
