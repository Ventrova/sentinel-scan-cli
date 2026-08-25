'use strict';

/**
 * Renders an Annex IV Lite compliance evidence pack (Markdown) from
 * sentinel-scan-cli scan result objects (the same shape `sentinel-scan`
 * and `sentinel-scan mcp` write to their `--output` JSON files).
 *
 * Used by `sentinel-scan evidence` (see bin/sentinel-scan.js). Kept as a
 * standalone, dependency-free module so the render step can also be
 * called directly on previously-saved scan JSON without re-running a scan.
 *
 * Crosswalk source: docs/product/findings-to-evidence-crosswalk.md.
 */

// --- Annex IV / questionnaire crosswalk -------------------------------------

const LLM_REMEDIATION = {
  LLM01: 'No action required for this category at this time; direct/role-play/obfuscation-based injection attempts were correctly refused.',
  LLM02: 'Add output-side filtering for known secret formats/patterns before the response leaves the model boundary; do not rely on system-prompt instructions alone to withhold secrets.',
  LLM05: 'Sanitize or strip markdown/link constructs from model output before rendering to the end user, or render output as plain text in contexts where exfiltration via rendered links/images is a risk.',
  LLM07: "Treat the system prompt as non-secret by design (assume it will eventually leak), and remove any embedded credentials, internal URLs, or secrets from it entirely; move those to a runtime-fetched, access-controlled store.",
};

const LLM_QA_ITEMS = {
  LLM01: 'Q17, Q19, Q24 (direct); Q18, Q26 (indirect)',
  LLM02: 'Q21',
  LLM05: 'Q21',
  LLM07: 'Q22',
};

const MCP_ANNEX_SECTION = {
  tool_description_injection: 'Section 3',
  indirect_injection_surface: 'Section 3',
  hidden_unicode_instructions: 'Section 3',
  tool_name_shadowing: 'Section 3, Section 5',
  hardcoded_credential: 'Section 5',
  unpinned_remote_source: 'Section 2, Section 6',
  missing_provenance: 'Section 2',
  tool_definition_drift: 'Section 6',
  excessive_agency_schema: 'Section 3, Section 5',
  overbroad_tool_scope: 'Section 5',
  missing_hitl_confirmation: 'Section 3',
  command_injection_risk: 'Section 3, Section 5',
  cross_origin_exfiltration: 'Section 3, Section 5',
  dos_resource_exhaustion: 'Section 3',
  homoglyph_typosquat: 'Section 3',
};

const MCP_QA_ITEMS = {
  tool_description_injection: 'Q17, Q26',
  indirect_injection_surface: 'Q26',
  hidden_unicode_instructions: 'Q17, Q26',
  tool_name_shadowing: 'Q12, Q30',
  hardcoded_credential: 'Q5, Q9',
  unpinned_remote_source: 'Q11, Q12, Q13, Q14',
  missing_provenance: 'Q11, Q13',
  tool_definition_drift: 'Q14, Q37, Q38',
  excessive_agency_schema: 'Q23, Q27',
  overbroad_tool_scope: 'Q27',
  missing_hitl_confirmation: 'Q28',
  command_injection_risk: 'Q23, Q25',
  cross_origin_exfiltration: 'Q2, Q9, Q25',
  dos_resource_exhaustion: '(gap - not in current Q&A bank; candidate Q41)',
  homoglyph_typosquat: 'Q12, Q30',
};

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

// Markdown table cells are `|`-delimited on a single line: an untrusted
// value (e.g. a tool name pulled straight from a scanned MCP manifest,
// which is attacker-controlled input by construction) containing a literal
// `|` or newline would otherwise split into extra columns/rows and could
// fabricate a fake table row in a document meant to be trustworthy audit
// evidence.
function escapeTableCell(value) {
  return String(value).replace(/\|/g, '\\|').replace(/\r?\n/g, ' ');
}

function llmCategoryCode(owaspCategory) {
  // "LLM02: Sensitive Information Disclosure" -> "LLM02"
  return owaspCategory.split(':')[0].trim();
}

function renderLlmSection(llm) {
  const s = llm.summary;
  const results = llm.results;
  const vulnerable = results.filter((r) => r.verdict === 'VULNERABLE');
  const scored = results.filter((r) => 'verdict' in r);
  const refused = scored.length - vulnerable.length;
  const categoriesCovered = [...new Set(scored.map((r) => llmCategoryCode(r.owasp_category)))].sort();

  const findingsRows = results.map((r) => {
    if (!('verdict' in r)) {
      return `| ${r.attack} | ${r.owasp_category} | ERROR | - | - |`;
    }
    const verdictCell = r.verdict === 'VULNERABLE' ? `**${r.verdict}**` : r.verdict;
    const leakCell = r.verdict === 'VULNERABLE' ? (r.leaked_secret_literal ? '**Yes**' : '**No**') : 'No';
    const sevCell = r.verdict === 'VULNERABLE' ? '**High**' : '-';
    return `| ${r.attack} | ${r.owasp_category} | ${verdictCell} | ${leakCell} | ${sevCell} |`;
  }).join('\n');

  const execSummary = `The target system was tested against ${s.num_attacks} adversarial prompts spanning ${categoriesCovered.length} OWASP LLM Top 10 categories (sentinel-scan-cli v${s.version}). ` +
    `${vulnerable.length} of ${s.num_attacks} attacks (${Math.round((vulnerable.length / s.num_attacks) * 100)}%) got past the system prompt` +
    (s.literal_leak_count ? `, ${s.literal_leak_count} of which resulted in a literal secret leak` : '') +
    `. ${refused} of ${s.num_attacks} (${Math.round((refused / s.num_attacks) * 100)}%) were correctly refused.`;

  const remediationRows = vulnerable.map((r) => {
    const code = llmCategoryCode(r.owasp_category);
    const fix = LLM_REMEDIATION[code] || 'Review this finding and apply category-appropriate remediation.';
    return `| ${r.attack} (${code}) | OPEN | ${fix} | Yes, before attestation |`;
  }).join('\n');

  const paragraph1 = `Direct-injection vectors (direct override, role-play jailbreak, fake system-tag injection, translation-trick obfuscation, base64 smuggling, hypothetical framing, authority impersonation, multi-turn setup, token smuggling, negation confusion, indirect tool-output injection) were tested per sentinel-scan-cli v${s.version}. ` +
    `${scored.filter((r) => llmCategoryCode(r.owasp_category) === 'LLM01').length} LLM01-mapped attacks were run; ` +
    `${scored.filter((r) => llmCategoryCode(r.owasp_category) === 'LLM01' && r.verdict === 'SAFE').length} were correctly refused. ` +
    `This evidences the "testing against foreseeable misuse" requirement of Annex IV Section 3 and answers questionnaire items ${LLM_QA_ITEMS.LLM01}.`;

  const coverageStatement = `sentinel-scan-cli v${s.version} directly evidences ${categoriesCovered.length} of the OWASP LLM Top 10 (2025) categories exercised in this run: ${categoriesCovered.join(', ')}. ` +
    `Categories not exercised by this corpus are disclosed as out of scope, not silently omitted, per Annex IV Section 1's completeness expectation.`;

  return {
    execSummary,
    findingsRows,
    remediationRows: remediationRows || '| (none) | - | No VULNERABLE findings in this run. | - |',
    paragraph1,
    coverageStatement,
    vulnerableCount: vulnerable.length,
    totalCount: s.num_attacks,
    refusedCount: refused,
    version: s.version,
    categoriesCovered,
  };
}

function renderMcpSection(mcp) {
  const s = mcp.summary;
  const findings = mcp.results;

  const findingsRows = findings.map((f) => {
    const annex = MCP_ANNEX_SECTION[f.heuristic] || '(unmapped)';
    const qa = MCP_QA_ITEMS[f.heuristic] || '(unmapped)';
    const sevCell = f.severity === 'HIGH' ? `**${f.severity}**` : f.severity;
    return `| ${f.heuristic} | ${escapeTableCell(f.tool)} | ${f.owasp_mcp_category || f.owasp_category} | ${sevCell} | ${annex} | ${qa} |`;
  }).join('\n');

  const bySev = s.findings_by_severity || {};
  const execSummary = `The MCP manifest was scanned with ${s.num_tools_scanned} tool(s) across ${s.num_servers_scanned} server(s) (sentinel-scan-cli mcp v${s.version}, static heuristic scan, no server execution). ` +
    `${s.num_findings} finding(s) were flagged: ${bySev.HIGH || 0} High, ${bySev.MEDIUM || 0} Medium, ${bySev.LOW || 0} Low.`;

  const supplyChainFindings = findings.filter((f) =>
    ['unpinned_remote_source', 'missing_provenance', 'tool_definition_drift'].includes(f.heuristic));
  const credentialFindings = findings.filter((f) => f.heuristic === 'hardcoded_credential');
  const agencyFindings = findings.filter((f) =>
    ['excessive_agency_schema', 'overbroad_tool_scope', 'missing_hitl_confirmation'].includes(f.heuristic));

  const supplyChainParagraph = `The MCP manifest scan flags ${supplyChainFindings.filter((f) => f.heuristic !== 'tool_definition_drift').length} tool source/provenance finding(s) (unpinned remote source or missing provenance metadata). ` +
    `This is the direct evidence input for Annex IV Section 2 (elements of the system and development process) regarding third-party component provenance, and answers questionnaire ${MCP_QA_ITEMS.unpinned_remote_source} / ${MCP_QA_ITEMS.missing_provenance}.`;

  const credentialParagraph = credentialFindings.length
    ? `The manifest scan flags ${credentialFindings.length} parameter/config field matching secret-bearing patterns not represented as a placeholder or environment reference. This is a direct finding for Annex IV Section 5 risk identification and answers questionnaire ${MCP_QA_ITEMS.hardcoded_credential}.`
    : `No hardcoded-credential findings in this run.`;

  const agencyParagraph = `${agencyFindings.length} tool/permission finding(s) were flagged for excessive agency (overbroad schema, wildcard scope, or missing human-in-the-loop confirmation on a sensitive capability). This is the structural precondition check for excessive-agency incidents (OWASP LLM06 / MCP06) and answers questionnaire ${MCP_QA_ITEMS.excessive_agency_schema} / ${MCP_QA_ITEMS.missing_hitl_confirmation}.`;

  return {
    execSummary,
    findingsRows,
    supplyChainParagraph,
    credentialParagraph,
    agencyParagraph,
    numFindings: s.num_findings,
    numTools: s.num_tools_scanned,
    numServers: s.num_servers_scanned,
    version: s.version,
    bySev,
  };
}

// args: { systemName, systemDescription, packId, scanDate, reportDate }
// llm: parsed `sentinel-scan --output <path>` JSON, or null to omit that section
// mcp: parsed `sentinel-scan mcp --output <path>` JSON, or null to omit that section
function renderPack(args, llm, mcp) {
  const packId = args.packId || `EP-${Date.now().toString(36).toUpperCase()}`;
  const systemName = args.systemName || 'REDACTED (client intake required)';
  const systemDescription = args.systemDescription || 'REDACTED (client intake required)';
  const scanDate = args.scanDate || todayIso();
  const reportDate = args.reportDate || todayIso();
  const version = (llm && llm.summary.version) || (mcp && mcp.summary.version) || 'unknown';

  const llmR = llm ? renderLlmSection(llm) : null;
  const mcpR = mcp ? renderMcpSection(mcp) : null;

  const scopeParts = [];
  if (llmR) scopeParts.push('Prompt injection resistance, sensitive information disclosure, system prompt leakage, output handling (OWASP LLM Top 10)');
  if (mcpR) scopeParts.push('MCP tool manifest static heuristic scan (OWASP MCP Top 10: prompt injection via descriptions, tool poisoning, excessive agency, supply chain, credential exposure)');
  const scope = scopeParts.join('; ') + '. Scope is limited to what an automated scan can evidence; it is not a full penetration test.';

  let out = '';
  out += `# Compliance Evidence Pack (Annex IV Lite)\n\n`;
  out += `**GENERATED DOCUMENT.** Rendered by \`sentinel-scan evidence\` from a real sentinel-scan-cli run. Every bracketed value below is filled from the scan JSON, not hand-typed boilerplate.\n\n`;
  out += `Produced by: Ventrova (sentinel-scan-cli)\n`;
  out += `Scan engine: sentinel-scan-cli v${version}\n\n`;
  out += `---\n\n`;

  out += `## 1. Cover and Scope\n\n`;
  out += `| Field | Value |\n|---|---|\n`;
  out += `| Evidence pack ID | ${packId} |\n`;
  out += `| Target system | ${systemName} |\n`;
  out += `| System description | ${systemDescription} |\n`;
  out += `| Scan date | ${scanDate} |\n`;
  out += `| Report date | ${reportDate} |\n`;
  out += `| Scope | ${scope} |\n`;
  out += `| Prepared for | Compliance/procurement use: EU AI Act Annex IV technical documentation slice, or vendor security questionnaire response |\n`;
  out += `| Prepared by | Ventrova, sentinel-scan-cli engine v${version} (not yet human-reviewed) |\n\n`;
  out += `---\n\n`;

  out += `## 2. Annex IV Slice (EU AI Act Technical Documentation)\n\n`;
  out += `The EU AI Act (Article 11(1), Annex IV) requires technical documentation covering nine areas. This pack evidences the sections a security scan can actually test; Sections 1, 4, 7, 8 (general system description, performance-metric appropriateness, harmonised standards, declaration of conformity) are organizational/legal artifacts outside scan scope and are called out below as gaps the customer's own team must fill.\n\n`;

  if (mcpR) {
    out += `**Annex IV, Section 2: Elements of the system and development process.**\n> ${mcpR.supplyChainParagraph}\n\n`;
  }

  out += `**Annex IV, Section 3: Monitoring, functioning, and control.**\n`;
  if (llmR) {
    out += `> ${llmR.paragraph1}\n\n`;
  }
  if (mcpR) {
    out += `> The MCP manifest scan additionally flags tool-description/schema prompt-injection surfaces, hidden-unicode instruction smuggling, and missing human-in-the-loop confirmation on sensitive tool capabilities as structural control-monitoring gaps (see Section 4 findings table).\n\n`;
  } else {
    out += `\n`;
  }

  out += `**Annex IV, Section 5: Risk management system (Article 9).**\n`;
  if (llmR) {
    out += `> The OWASP LLM Top 10-mapped findings table in Section 4 is the risk-identification input to a formal risk management process: each finding is scored SAFE/VULNERABLE, categorized by OWASP LLM risk class, and given a severity. ${llmR.vulnerableCount} of ${llmR.totalCount} attacks scored VULNERABLE in this run.\n\n`;
  }
  if (mcpR) {
    out += `> ${mcpR.credentialParagraph} ${mcpR.agencyParagraph}\n\n`;
  }

  if (mcpR) {
    out += `**Annex IV, Section 6: Lifecycle changes.**\n> This pack establishes a baseline (${mcpR.numFindings} finding(s) across ${mcpR.numTools} tool(s), ${mcpR.numServers} server(s)) as of ${scanDate}. Re-run \`sentinel-scan mcp --baseline\` to produce an actual before/after record for future scans.\n\n`;
  }

  out += `**Annex IV, Section 9: Post-market monitoring.**\n> A re-attestation cadence (periodic re-scan against the same corpus/manifest) is the mechanism by which a customer can show an auditor a recurring, dated testing cadence rather than a one-time snapshot.\n\n`;

  out += `**Not covered by this pack** (customer must source separately): Annex IV Section 1 (general system description), Section 4 (performance metric appropriateness), Section 7 (harmonised standards applied), Section 8 (EU declaration of conformity).\n\n`;
  out += `---\n\n`;

  out += `## 3. Executive Summary\n\n`;
  if (llmR) out += `${llmR.execSummary}\n\n`;
  if (mcpR) out += `${mcpR.execSummary}\n\n`;
  out += `---\n\n`;

  if (llmR) {
    out += `## 4. Prompt-Injection Findings Table (OWASP LLM Top 10-mapped)\n\n`;
    out += `Source: sentinel-scan-cli v${llmR.version}, ${llmR.totalCount} attacks, ${llmR.vulnerableCount} vulnerable.\n\n`;
    out += `| Attack | OWASP LLM Category | Verdict | Secret Literal Leaked | Severity |\n|---|---|---|---|---|\n`;
    out += `${llmR.findingsRows}\n\n`;
    out += `**Summary counts:** ${llmR.totalCount} attacks run, ${llmR.vulnerableCount} vulnerable (${Math.round((llmR.vulnerableCount / llmR.totalCount) * 100)}%), ${llmR.refusedCount} correctly refused.\n\n`;
    out += `**Coverage statement:** ${llmR.coverageStatement}\n\n`;
    out += `---\n\n`;
  }

  if (mcpR) {
    out += `## 5. MCP Manifest Findings Table (OWASP MCP Top 10-mapped)\n\n`;
    out += `Source: sentinel-scan-cli mcp v${mcpR.version}, ${mcpR.numTools} tools / ${mcpR.numServers} servers scanned, ${mcpR.numFindings} finding(s) (${mcpR.bySev.HIGH || 0} High, ${mcpR.bySev.MEDIUM || 0} Medium, ${mcpR.bySev.LOW || 0} Low).\n\n`;
    out += `| Heuristic | Tool/Server | OWASP Category | Severity | Annex IV Section | Questionnaire Q# |\n|---|---|---|---|---|---|\n`;
    out += `${mcpR.findingsRows}\n\n`;
    out += `---\n\n`;
  }

  out += `## 6. Human Attestation Block\n\n`;
  out += `This section is signed by a named human at the customer organization, not by Ventrova or by the scan tool. sentinel-scan-cli and this evidence pack provide test results; only the customer's own accountable engineer or security owner can attest to what remediation action was taken and why residual risk (if any) is accepted.\n\n`;
  out += '```\n';
  out += 'Attestation\n\n';
  out += `I confirm that the findings in this Compliance Evidence Pack\n(Evidence Pack ID: ${packId}) were reviewed by the undersigned, and that:\n\n`;
  out += '  [ ] All VULNERABLE findings have been remediated and re-tested, OR\n';
  out += '  [ ] The following VULNERABLE findings remain open with documented\n';
  out += '      compensating controls or accepted residual risk (attach rationale):\n';
  out += '      ______________________________________________________\n\n';
  out += 'Name:            ______________________________\n';
  out += 'Title:           ______________________________\n';
  out += 'Organization:    ______________________________\n';
  out += 'Date:            ______________________________\n';
  out += 'Signature:       ______________________________\n';
  out += '```\n\n';
  out += `*Ventrova does not pre-fill or sign this section; a scan tool cannot attest to organizational remediation decisions on a customer's behalf.*\n\n`;
  out += `---\n\n`;

  if (llmR) {
    out += `## 7. Remediation Status Appendix (Prompt-Injection Findings)\n\n`;
    out += `| Finding | Status | Recommended Fix | Re-test Required |\n|---|---|---|---|\n`;
    out += `${llmR.remediationRows}\n\n`;
    out += `---\n\n`;
  }

  out += `## Appendix: Raw Scan Evidence\n\n`;
  out += `Full raw sentinel-scan-cli JSON output is included as a separate machine-readable attachment (\`${llmR ? 'llm-scan-result.json' : ''}${llmR && mcpR ? ', ' : ''}${mcpR ? 'mcp-scan-result.json' : ''}\`), so an auditor who wants to verify the tables above can inspect the underlying scan output directly.\n\n`;
  out += `---\n\n`;
  out += `*Generated by \`sentinel-scan evidence\` v${version}. Grounding sources: docs/product/findings-to-evidence-crosswalk.md. This is a scan-derived draft, not a customer deliverable - review before sharing with an auditor or customer.*\n`;

  return out;
}

module.exports = {
  renderPack,
  renderLlmSection,
  renderMcpSection,
  escapeTableCell,
  llmCategoryCode,
  todayIso,
  LLM_REMEDIATION,
  LLM_QA_ITEMS,
  MCP_ANNEX_SECTION,
  MCP_QA_ITEMS,
};
