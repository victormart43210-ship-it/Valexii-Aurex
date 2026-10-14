/** Pure, dependency-free branded email bodies. All dynamic values are HTML-escaped. */
export function esc(value: string): string {
  return value.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);
}

function shell(title: string, body: string): string {
  return `<!doctype html><html lang="en"><body style="margin:0;background:#ffffff;font-family:Arial,Helvetica,sans-serif;color:#0b1220">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:24px">
<table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%">
<tr><td style="background:#07111f;padding:20px 24px;border-bottom:3px solid #c9a24a">
<span style="color:#ffffff;font-size:18px;letter-spacing:2px;font-weight:bold">VALEXII.AI</span>
<span style="color:#5fe3e0;font-size:12px;letter-spacing:1px;margin-left:8px">BCXME THE CHANGE</span></td></tr>
<tr><td style="padding:28px 24px;border:1px solid #e3e8ef;border-top:0">
<h1 style="font-size:20px;margin:0 0 16px;color:#07111f">${esc(title)}</h1>${body}
<p style="font-size:12px;line-height:18px;color:#5b6675;margin-top:28px">VALEXII.AI · developmental research and products. BCXMET is in development and does not currently protect any device.</p>
</td></tr></table></td></tr></table></body></html>`;
}

const p = (t: string) => `<p style="font-size:14px;line-height:22px;margin:0 0 12px">${t}</p>`;

export function renderInquiryNotification(i: {
  kind: string; name: string; email: string; organization?: string; category: string; message: string; id: string;
}) {
  const subject = `[${i.kind === "partnership" ? "Partnership" : "Contact"}] ${i.category} — ${i.name}`.slice(0, 160);
  const html = shell("New website inquiry", [
    p(`<strong>Type:</strong> ${esc(i.kind)} · <strong>Category:</strong> ${esc(i.category)}`),
    p(`<strong>Name:</strong> ${esc(i.name)}<br><strong>Email:</strong> ${esc(i.email)}${i.organization ? `<br><strong>Organization:</strong> ${esc(i.organization)}` : ""}`),
    `<div style="white-space:pre-wrap;font-size:14px;line-height:22px;background:#f5f7fa;padding:12px;border-left:3px solid #5fe3e0">${esc(i.message)}</div>`,
    p(`<span style="font-size:12px;color:#5b6675">Reference ${esc(i.id)}. Reply goes directly to the sender.</span>`),
  ].join(""));
  return { subject, html };
}

export function renderInquiryReceipt(name: string) {
  return {
    subject: "We received your message — VALEXII.AI",
    html: shell(`Thank you, ${name}`, [
      p("Your message reached VALEXII.AI and was stored securely. A person reads every inquiry; there is no guaranteed response time."),
      p("Please keep follow-ups non-confidential: do not send credentials, private repository contents or unpublished patentable details."),
      p("No partnership, investment offering, funding or product access is implied by this acknowledgement."),
    ].join("")),
  };
}

export function renderEarlyAccessConfirm(confirmUrl: string) {
  return {
    subject: "Confirm your BCXMET early-access interest",
    html: shell("Confirm your early-access interest", [
      p("Someone (hopefully you) asked to hear about BCXMET early-access opportunities. Confirm to be added:"),
      `<p style="margin:20px 0"><a href="${esc(confirmUrl)}" style="background:#5fe3e0;color:#07111f;padding:12px 20px;text-decoration:none;font-weight:bold;border-radius:4px">Confirm interest</a></p>`,
      p("If you did not request this, ignore this email and nothing further happens."),
      p("Interest is not a beta invitation, download, subscription or protection. BCXMET has no active public beta today."),
    ].join("")),
  };
}
