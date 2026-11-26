# PDF Study Agent

A web app where you upload study PDFs and ask questions. Answers cite the document name and page number.

## Files

- `app.py` - the web page (upload, chat, sources)
- `pdf_utils.py` - reads PDFs, splits them into chunks, finds relevant chunks
- `ai_utils.py` - sends questions and passages to Gemini
- `requirements.txt` - Python packages the host installs automatically

## Deploy on Streamlit Community Cloud (from your phone)

1. **Create a GitHub repository.** Sign in at github.com, tap **+** then **New repository**, name it `pdf-study-agent`, and set it to **Public** or **Private**. Tap **Add file > Upload files** and upload all four files above. Tap **Commit changes**.
2. **Deploy.** Go to share.streamlit.io, sign in with GitHub, tap **Create app**, choose your repository, and set the main file path to `app.py`.
3. **Add your key.** Before deploying, open **Advanced settings > Secrets** and paste this, replacing the placeholder with your real key:

   ```
   GEMINI_API_KEY = "paste-your-key-here"
   ```

4. Tap **Deploy**. After a minute or two you get a link. Open it in Chrome, tap the menu (⋮), and choose **Add to Home screen**.

Never put your real key in any file you upload to GitHub.

## Testing checklist

1. Upload a text-based PDF from the sidebar. Check that its name and page count appear.
2. Ask a question you know is in the PDF. Check that the answer names a page.
3. Open **Passages used** under the answer and confirm the page number matches the original PDF.
4. Ask something not in the PDF. The app should say the PDFs do not seem to cover it.

## Known limits (version 1)

- Search uses keyword matching, not AI embeddings. It works well for specific terms and less well for vague questions.
- Scanned PDFs without text are detected but not read yet (OCR comes later).
- Chat history and uploads are cleared when the app restarts. Saving them to a database comes later.
- Free-tier Gemini limits apply. If you see a quota error, wait a minute or try the next day.
- Always spot-check important answers against the original pages before an exam.

## Running on a computer (optional)

```
pip install -r requirements.txt
set GEMINI_API_KEY=your-key   (Windows)  or  export GEMINI_API_KEY=your-key   (Mac/Linux)
streamlit run app.py
```
