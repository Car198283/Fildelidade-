export function formatBirthdayInput(value) {
  const digits = String(value || "").replace(/\D/g, "").slice(0, 8);

  if (digits.length <= 2) return digits;
  if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`;

  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
}

export function normalizeBirthdayForInput(value) {
  if (!value) return "";

  const text = String(value);
  const isoMatch = text.match(/^(\d{4})-(\d{2})-(\d{2})/);

  if (isoMatch) {
    return `${isoMatch[3]}/${isoMatch[2]}/${isoMatch[1]}`;
  }

  return formatBirthdayInput(text);
}

export function birthdayInputToApi(value) {
  if (!value) return null;

  const text = String(value).trim();
  const brMatch = text.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);

  if (brMatch) {
    return `${brMatch[3]}-${brMatch[2]}-${brMatch[1]}`;
  }

  return text;
}
