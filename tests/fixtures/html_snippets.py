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
