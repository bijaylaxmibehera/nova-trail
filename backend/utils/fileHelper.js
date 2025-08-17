const fs = require("fs");
const path = require("path");
const pdfParse = require("pdf-parse");
const mammoth = require("mammoth");

// Helper: extract text
async function extractTextFromFile(filePath, mimetype) {
  const ext = path.extname(filePath).toLowerCase();
  try {
    if (ext === ".pdf") {
      const data = fs.readFileSync(filePath);
      const parsed = await pdfParse(data);
      return parsed.text || "";
    } else if (ext === ".docx" || ext === ".doc") {
      if (ext === ".docx") {
        const result = await mammoth.extractRawText({ path: filePath });
        return result.value || "";
      } else {
        // .doc fallback
        const buf = fs.readFileSync(filePath);
        return buf.toString("utf8");
      }
    } else if (ext === ".txt") {
      return fs.readFileSync(filePath, "utf8");
    }
    return "";
  } catch (err) {
    console.error("Text extraction error:", err);
    return "";
  }
}

module.exports = { extractTextFromFile };
