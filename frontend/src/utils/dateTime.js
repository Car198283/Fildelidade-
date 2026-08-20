const APP_TIME_ZONE = "America/Sao_Paulo";

export function parseApiDateTime(value) {
  if (!value) return null;

  const text = String(value).trim();
  const hasTimeZone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(text);
  const parsed = new Date(hasTimeZone ? text : `${text}Z`);

  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export function formatApiDateTime(value) {
  const date = parseApiDateTime(value);
  return date
    ? date.toLocaleString("pt-BR", { timeZone: APP_TIME_ZONE })
    : "-";
}

export function formatApiDate(value) {
  const date = parseApiDateTime(value);
  return date
    ? date.toLocaleDateString("pt-BR", { timeZone: APP_TIME_ZONE })
    : "-";
}
