from __future__ import annotations

import json
from typing import Any, Callable

from backend.artifacts.filesystem import ArtifactRun
from backend.pipelines.authorship import add_author_credit
from backend.pipelines.common import (
    PipelineError,
    PipelineResult,
    extract_fenced_or_raw,
    format_citations,
    format_log,
)
from backend.pipelines.html_to_pdf import (
    A4_PAGE,
    ConvertError,
    HtmlToPdfConverter,
)
from backend.providers.base import (
    ModelProviderError,
    TextGenerationProvider,
    TextGenerationRequest,
)
from backend.timing import RunTimingRecorder, measure_stage


def run_essay_html_pipeline(
    *,
    artifact_run: ArtifactRun,
    model_profile: dict[str, Any],
    model_provider: TextGenerationProvider,
    pdf_converter: HtmlToPdfConverter,
    task_text: str,
    context_bundle: str,
    output_preference: str | None,
    options: dict[str, Any] | None,
    search: dict[str, Any],
    max_output_tokens: int,
    emit_event: Callable[[str, str], None] | None = None,
    timing: RunTimingRecorder | None = None,
) -> PipelineResult:
    log_lines = [
        "Pipeline: essay_html",
        f"Output preference: {output_preference or 'pdf'}",
        "Stage: generate_source",
    ]
    system_prompt, user_prompt = build_essay_html_prompt(
        task_text=task_text,
        context_bundle=context_bundle,
        options=options or {},
        search=search,
    )
    if emit_event:
        emit_event("generate_source", "Generating essay HTML source")

    try:
        with measure_stage(timing, "provider_generation"):
            raw_output = model_provider.generate_text(
                TextGenerationRequest(
                    profile=model_profile,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_output_tokens=max_output_tokens,
                    temperature=0.2,
                )
            )
    except ModelProviderError as exc:
        raise PipelineError(
            exc.code,
            exc.message,
            stage="generate_source",
            log_lines=log_lines,
        ) from exc
    except Exception as exc:
        raise PipelineError(
            "provider_unavailable",
            "The model provider request failed.",
            stage="generate_source",
            log_lines=log_lines,
        ) from exc

    source = extract_fenced_or_raw(raw_output, accepted_languages={"html", "htm"})
    source = add_author_credit(source.strip()) + "\n"
    html_path = artifact_run.write_output(
        "main.html",
        source,
        kind="source",
        media_type="text/html",
    )
    log_lines.extend(["Output: output/main.html", "Stage: convert_pdf"])
    if emit_event:
        emit_event("convert_pdf", "Converting essay HTML to PDF")

    pdf_path = artifact_run.run_dir / "output" / "main.pdf"
    try:
        with measure_stage(timing, "convert_pdf"):
            convert_result = pdf_converter.convert(
                html_path=html_path,
                pdf_path=pdf_path,
                page_config=A4_PAGE,
            )
    except ConvertError as exc:
        artifact_run.write_log("convert.log", exc.log_text)
        raise PipelineError(
            "convert_failed",
            exc.message,
            stage="convert_pdf",
            log_lines=log_lines,
        ) from exc
    except Exception as exc:
        artifact_run.write_log(
            "convert.log",
            "HTML-to-PDF converter raised an unexpected error.\n",
        )
        raise PipelineError(
            "convert_failed",
            "HTML-to-PDF conversion failed.",
            stage="convert_pdf",
            log_lines=log_lines,
        ) from exc

    artifact_run.write_log("convert.log", convert_result.log_text)
    artifact_run.write_output(
        "main.pdf",
        convert_result.pdf_path.read_bytes(),
        kind="pdf",
        media_type="application/pdf",
    )
    log_lines.extend(["Convert: pdf_ok", "Output: output/main.pdf"])
    return PipelineResult(log_text=format_log(log_lines))


def build_essay_html_prompt(
    *,
    task_text: str,
    context_bundle: str,
    options: dict[str, Any],
    search: dict[str, Any],
) -> tuple[str, str]:
    system_prompt = (
        "You are an expert teaching assistant writing complete academic essay and "
        "report deliverables as self-contained HTML documents. Return only the "
        "requested HTML source, with no surrounding explanation."
    )
    output_instruction = (
        "Return one complete self-contained HTML document. It must start with "
        "<!doctype html> and include <html>, <head>, and <body>. Include all CSS "
        "inside a <style> element: use a readable serif academic print layout, "
        "clear heading hierarchy, careful paragraph spacing, and CSS "
        "@page { size: A4; margin: 20mm; }. Do not use external stylesheet links, "
        "remote images, or remote HTTP(S) assets. If mathematical notation is "
        "needed, include inline KaTeX-compatible markup and any needed minimal "
        "KaTeX styling inline in the document; do not fetch KaTeX from a CDN at "
        "render time. Use inline SVG or CSS for diagrams. Cite any provided web "
        "sources in a References section using ordinary HTML. Do not wrap the "
        "answer in Markdown fences."
    )
    assignment_instruction = (
        "When the task is the BA3073 'From AI Agent to Cloud Service' assignment, "
        "write an evidence-based deployment report in English unless the user "
        "requests another language. Respect the user's requested length; aim "
        "for a concise report and never exceed 20 "
        "pages including cover, references, screenshots, and appendices. Use "
        "readable 11-12pt text, compact tables, and sensible page breaks; do not "
        "shrink text to conceal excess length. Organize the report into: title "
        "and supplied student details; abstract; system architecture; Task 1 "
        "local Docker deployment and verification; report-prompt improvements; "
        "Task 2 Linux image build, ACR push/pull and ECS verification; "
        "assignment scope and any explicitly waived requirements; "
        "security, persistence and cost analysis; limitations and improvements; "
        "conclusion; references and an evidence checklist. Explain FastAPI, "
        "the browser UI, SQLite, mounted data/workspace directories, model API "
        "calls, and HTML-to-PDF conversion. Identify the actual model provider "
        "from the supplied evidence (for example DeepSeek instead of Qwen). "
        "Explain each command's purpose and its observed result, distinguishing "
        "expected output from measured output. Compare the original generic "
        "essay instructions with the revised assignment-specific instructions. "
        "Use only supplied evidence for claims of successful deployment. Never "
        "invent commands run, dates, IP addresses, domains, student identity, "
        "screenshots, HTTP results, costs or test outcomes. Mark absent evidence "
        "as NOT YET VERIFIED and unfinished tasks as INCOMPLETE; do not describe "
        "planned work in the past tense. Include captions and references to "
        "local and ECS screenshots with the address bar visible, the actual "
        "HTTPS URL and proxy access-control evidence only when those are required. "
        "Respect explicit instructor scope changes supplied by the user: if domain, "
        "HTTPS and reverse-proxy authentication are waived, label Task 3 NOT REQUIRED "
        "under the revised scope, not INCOMPLETE. Do not invent a domain or claim "
        "Nginx/TLS was deployed. Do not infer any redistribution of marks. If images "
        "are not available, insert clearly labelled missing-evidence boxes, "
        "never fabricated browser screenshots. Explain that Task 2 port 14242 "
        "should be restricted to the student's public IP; claim that restriction "
        "was verified only when security-group evidence is supplied. When Task 3 "
        "is waived, describe direct HTTP access as a restricted teaching demo, "
        "with TLS and a reverse proxy as future improvements. Otherwise document "
        "Task 3 DNS, Nginx, TLS/Certbot and independent access control, including "
        "ports 80/443 and removal of public access to 14242. Explain why "
        "BNBU login alone is insufficient. Discuss API-key handling, encrypted "
        "personal keys and the external encryption key, backup/restore, TLS "
        "renewal, least privilege, cloud/API cost control and service shutdown. "
        "Exclude all secrets, passwords, tokens and private keys. End with a "
        "checklist for the report, whole-project GitHub URL, local-ui-check.txt "
        "and ecs-docker-check.txt. Treat a report with missing deployment "
        "evidence as a draft, not a completed submission. For other essay "
        "assignments, follow their requested structure instead."
    )
    user_prompt = "\n\n".join(
        [
            "[Assignment Task]\n" + task_text.strip(),
            "[Prepared Context]\n" + context_bundle.strip(),
            "[Search Citations]\n" + format_citations(search),
            "[Options]\n" + json.dumps(options, sort_keys=True),
            "[BA3073 Report Guidance]\n" + assignment_instruction,
            "[Output Contract]\n" + output_instruction,
        ]
    )
    return system_prompt, user_prompt
