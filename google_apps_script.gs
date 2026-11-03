const SPREADSHEET_ID = "1o-fNJFaLhUBlvTntAr7ZU84RHxm-IkLwcyX7DAhUF7s";
const ANNUAL_SHEET_NAME = "各年度活動報名人數總表";
const CATEGORY_SHEET_NAME = "各類活動報名人數總計表";
const ANNUAL_HEADERS = [
  "年份",
  "祭改人數",
  "300元光明燈",
  "500元光明燈",
  "300元太歲",
  "500元太歲",
  "1000元年斗",
  "3000元年斗",
  "5000元年斗",
  "6000元年斗",
  "全家補運人數",
  "補財庫人數",
  "六月補運人數",
  "九月補運人數",
  "六月補財庫人數",
  "九月補財庫人數",
  "普度人數",
];
const CATEGORY_HEADERS = [
  "年份",
  "祭改總計",
  "光明燈總計",
  "太歲總計",
  "正月年斗總計",
  "三月全家補運及補財庫總計",
  "個人補運及補財庫總計",
  "普度總計",
];

function doPost(event) {
  try {
    const request = JSON.parse(event.postData.contents);
    authorize_(request.token);

    if (request.action === "load") {
      return jsonOutput_({
        ok: true,
        annual_summary: readAnnualSummary_(),
      });
    }

    if (request.action === "sync") {
      validateTable_(request.annual_summary, ANNUAL_HEADERS);
      validateTable_(request.category_totals, CATEGORY_HEADERS);
      writeTable_(ANNUAL_SHEET_NAME, request.annual_summary, ANNUAL_HEADERS);
      writeTable_(
        CATEGORY_SHEET_NAME,
        request.category_totals,
        CATEGORY_HEADERS,
      );
      return jsonOutput_({ ok: true });
    }

    throw new Error("Unsupported action.");
  } catch (error) {
    return jsonOutput_({
      ok: false,
      error: String(error && error.message ? error.message : error),
    });
  }
}

function authorize_(providedToken) {
  const expectedToken = PropertiesService.getScriptProperties().getProperty(
    "SYNC_TOKEN",
  );
  if (!expectedToken || providedToken !== expectedToken) {
    throw new Error("Unauthorized.");
  }
}

function readAnnualSummary_() {
  const sheet = getOrCreateSheet_(ANNUAL_SHEET_NAME);
  const values = sheet.getDataRange().getValues();
  if (values.length < 2 || values[0].every((value) => value === "")) {
    return null;
  }

  const headers = values[0].map(String);
  if (
    headers.length !== ANNUAL_HEADERS.length ||
    !ANNUAL_HEADERS.every((header, index) => headers[index] === header)
  ) {
    throw new Error(
      `工作表「${ANNUAL_SHEET_NAME}」欄位不符，請由系統同步建立表頭。`,
    );
  }

  const rows = values
    .slice(1)
    .filter((row) => row[0] !== "")
    .map((row) => row.map((value) => Number(value)));
  rows.forEach((row) => validateNumericRow_(row, ANNUAL_HEADERS.length));
  return { headers: ANNUAL_HEADERS, rows: rows };
}

function validateTable_(table, expectedHeaders) {
  if (
    !table ||
    !Array.isArray(table.headers) ||
    !Array.isArray(table.rows) ||
    table.headers.length !== expectedHeaders.length ||
    !expectedHeaders.every(
      (header, index) => table.headers[index] === header,
    )
  ) {
    throw new Error("報表欄位格式不正確。");
  }
  table.rows.forEach((row) =>
    validateNumericRow_(row, expectedHeaders.length),
  );
}

function validateNumericRow_(row, expectedLength) {
  if (
    !Array.isArray(row) ||
    row.length !== expectedLength ||
    row.some(
      (value) =>
        typeof value !== "number" ||
        !Number.isSafeInteger(value) ||
        value < 0,
    )
  ) {
    throw new Error("報表資料必須是非負整數。");
  }
}

function writeTable_(sheetName, table, expectedHeaders) {
  const sheet = getOrCreateSheet_(sheetName);
  const values = [expectedHeaders, ...table.rows];
  sheet.clearContents();
  sheet.getRange(1, 1, values.length, expectedHeaders.length).setValues(values);
}

function getOrCreateSheet_(name) {
  const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  return spreadsheet.getSheetByName(name) || spreadsheet.insertSheet(name);
}

function jsonOutput_(value) {
  return ContentService.createTextOutput(JSON.stringify(value)).setMimeType(
    ContentService.MimeType.JSON,
  );
}
