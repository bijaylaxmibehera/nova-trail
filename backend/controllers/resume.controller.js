const fs = require("fs");
const axios = require("axios");
const { extractTextFromFile } = require("../utils/fileHelper");

// Controller: Upload & Process Resume
uploadResume = async (req, res) => {
  if (!req.file) return res.status(400).json({ message: "Resume file required" });

  const filePath = req.file.path;
  try {
    const resumeText = await extractTextFromFile(filePath, req.file.mimetype);

    const payload = {
      resume: resumeText,
      job_posting: req.body.job_posting || "",
      location: req.body.location || "India",
    };

    const mlUrl = process.env.ML_API_URL || "http://127.0.0.1:5001/analyze-job";
    const mlResp = await axios.post(mlUrl, payload, { timeout: 30000 });

    // Delete uploaded file
    fs.unlink(filePath, (err) => {
      if (err) console.warn("Failed to delete upload:", err);
    });

    return res.json(mlResp.data);
  } catch (err) {
    console.error("Error in uploadResume:", err);
    try { fs.unlinkSync(filePath); } catch (e) {}
    return res.status(500).json({ message: "Server error while processing resume" });
  }
};

module.exports =  uploadResume ;
