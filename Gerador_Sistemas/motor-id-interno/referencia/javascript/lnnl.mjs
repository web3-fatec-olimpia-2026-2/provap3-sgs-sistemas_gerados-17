/**
 * LNNL — identificador interno legível por humanos (implementação de referência, ES2020).
 *
 * Formato canônico de 14 caracteres, exibido como LNNL-LNNL-LNL-LNL
 * (L = letra A–Z maiúscula; N = dígito 1–9, sem o 0 para não confundir com O).
 *   posições 2–3: código do tipo (11–99 sem zero; 93 reservado)
 *   posições 6–7: dois verificadores = resto módulo 79 da soma ponderada dos outros 12
 *
 * Sem dependências. Roda no Node (>= 16) e no navegador. Especificação: ../../RFC-LNNL.md
 */

export const LETRAS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
export const DIGITOS = '123456789';
export const MASCARA = 'LNNL-LNNL-LNL-LNL';
export const CLASSES = 'LNNLLNNLLNLLNL';
/** Pesos normativos (posições 1–5 e 8–14). Nunca mudam. */
export const PESOS = Object.freeze([71, 63, 76, 57, 31, 1, 11, 15, 37, 13, 58, 2]);
export const MODULO = 79;
export const TIPO_RESERVADO = '93';
export const REGEX_CANONICA = /^[A-Z][1-9]{2}[A-Z]{2}[1-9]{2}[A-Z]{2}[1-9][A-Z]{2}[1-9][A-Z]$/;

export const ERROS = Object.freeze({
  TAMANHO_INVALIDO: 'TAMANHO_INVALIDO',
  FORMATO_INVALIDO: 'FORMATO_INVALIDO',
  TIPO_RESERVADO: 'TIPO_RESERVADO',
  TIPO_INCOMPATIVEL: 'TIPO_INCOMPATIVEL',
  VERIFICADOR_INVALIDO: 'VERIFICADOR_INVALIDO',
});

/** Maiúsculas e somente A–Z/0–9 (remove hífens, espaços e separadores). */
export function normalizar(valor) {
  if (valor == null) return '';
  return String(valor).trim().toUpperCase().replace(/[^A-Z0-9]/g, '');
}

/** Máscara de exibição 4-4-3-3. */
export function formatar(valor) {
  const c = normalizar(valor);
  if (c.length !== 14) return c;
  return `${c.slice(0, 4)}-${c.slice(4, 8)}-${c.slice(8, 11)}-${c.slice(11)}`;
}

/** A=1 … Z=26; '1'..'9' = 1..9. */
export function valorCaractere(ch) {
  const code = ch.charCodeAt(0);
  if (code >= 65 && code <= 90) return code - 64;
  if (code >= 49 && code <= 57) return code - 48;
  throw new RangeError(`Caractere fora do alfabeto LNNL: ${ch}`);
}

/** [d1, d2] a partir dos 12 caracteres de dados (posições 1–5 e 8–14). */
export function calcularVerificadores(dados12) {
  if (dados12.length !== 12) throw new RangeError('São necessários 12 caracteres de dados.');
  let soma = 0;
  for (let i = 0; i < 12; i++) soma += PESOS[i] * valorCaractere(dados12[i]);
  const resto = soma % MODULO;
  return [Math.floor(resto / 9) + 1, (resto % 9) + 1];
}

export function montar(dados12) {
  const [d1, d2] = calcularVerificadores(dados12);
  return `${dados12.slice(0, 5)}${d1}${d2}${dados12.slice(5)}`;
}

export function extrairTipo(valor) {
  const c = normalizar(valor);
  return c.length >= 3 ? c.slice(1, 3) : '';
}

function tipoStr(tipo) {
  const t = typeof tipo === 'number' ? String(tipo).padStart(2, '0') : String(tipo);
  if (!/^[1-9]{2}$/.test(t)) throw new RangeError(`Tipo inválido: ${tipo}. Use 11–99 sem zero.`);
  return t;
}

/** { valido, erro, canonico } — erros na ordem normativa. */
export function validar(valor, tipoEsperado = null) {
  const c = normalizar(valor);
  if (c.length !== 14) return { valido: false, erro: ERROS.TAMANHO_INVALIDO, canonico: '' };
  if (!REGEX_CANONICA.test(c)) return { valido: false, erro: ERROS.FORMATO_INVALIDO, canonico: '' };
  const tipo = c.slice(1, 3);
  if (tipo === TIPO_RESERVADO) return { valido: false, erro: ERROS.TIPO_RESERVADO, canonico: '' };
  if (tipoEsperado != null && tipo !== tipoStr(tipoEsperado)) {
    return { valido: false, erro: ERROS.TIPO_INCOMPATIVEL, canonico: '' };
  }
  const [d1, d2] = calcularVerificadores(c.slice(0, 5) + c.slice(7));
  if (c.slice(5, 7) !== `${d1}${d2}`) return { valido: false, erro: ERROS.VERIFICADOR_INVALIDO, canonico: '' };
  return { valido: true, erro: null, canonico: c };
}

/** Sorteio uniforme com rejeição (sem viés de módulo), usando crypto.getRandomValues. */
function sortear(alfabeto) {
  const limite = 256 - (256 % alfabeto.length);
  const buf = new Uint8Array(1);
  for (;;) {
    globalThis.crypto.getRandomValues(buf);
    if (buf[0] < limite) return alfabeto[buf[0] % alfabeto.length];
  }
}

/**
 * Gera um identificador válido para o tipo. A unicidade é responsabilidade do
 * armazenamento (restrição única + nova tentativa em caso de colisão).
 */
export function gerar(tipo, sorteio = sortear) {
  const t = tipoStr(tipo);
  if (t === TIPO_RESERVADO) throw new RangeError(`O tipo ${TIPO_RESERVADO} é reservado.`);
  const L = () => sorteio(LETRAS);
  const N = () => sorteio(DIGITOS);
  const dados = L() + t + L() + L() + L() + L() + N() + L() + L() + N() + L();
  return montar(dados);
}

/** Identificadores válidos a um caractere de distância (para atendimento; confirmar no armazenamento). */
export function candidatosCorrecao(valor) {
  const c = normalizar(valor);
  if (c.length !== 14 || !REGEX_CANONICA.test(c) || validar(c).valido) return [];
  const saida = [];
  for (let i = 0; i < 14; i++) {
    const alfabeto = CLASSES[i] === 'L' ? LETRAS : DIGITOS;
    for (const ch of alfabeto) {
      if (ch === c[i]) continue;
      const candidato = c.slice(0, i) + ch + c.slice(i + 1);
      if (validar(candidato).valido) saida.push(candidato);
    }
  }
  return saida;
}
