"""Sample Canvas HTML snippets for html utils tests."""

ASSIGNMENT_DESCRIPTION_HTML = """
<div>
  <p>Read the <a href="/courses/100001/pages/week-1">Week 1 page</a>.</p>
  <p>Download:
    <a href="/courses/100001/files/500001/download?wrap=1"
       data-api-endpoint="/api/v1/courses/100001/files/500001"
       class="instructure_file_link">worksheet.pdf</a>
  </p>
  <p>Also see <a href="https://example.edu/resource">external resource</a>.</p>
  <script>alert('ignore me');</script>
  <style>.hidden { display: none; }</style>
</div>
"""

SYLLABUS_HTML = """
<h1>Syllabus</h1>
<p>Assignments live in <a href="/courses/100001/assignments/200001">Homework 1</a>.</p>
"""

DANGEROUS_HTML = """
<div>
  <iframe src="https://evil.example/embed">iframe text</iframe>
  <object data="evil.swf">object text</object>
  <embed src="evil.swf">embed text</embed>
  <noscript>noscript text</noscript>
  <template>template text</template>
  <svg><title>svg title</title></svg>
  <a href="javascript:alert(1)">bad link</a>
  <p>visible paragraph</p>
</div>
"""
