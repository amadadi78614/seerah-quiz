/* ═══════════════════════════════════════════════════════════
   Seerah Quiz — Certificate Generator
   Draws a completion certificate on a <canvas> element
   and triggers a PNG download.
   ═══════════════════════════════════════════════════════════ */

function generateCertificate(opts) {
  /*
    opts = {
      name:       string  — student name
      worldName:  string  — e.g. "The Prophets"
      worldEmoji: string  — e.g. "📜"
      score:      number  — percentage 0-100
      total:      number  — total questions answered
      date:       string  — formatted date string
      canvasId:   string  — id of <canvas> element
    }
  */
  const c = document.getElementById(opts.canvasId || 'cert-canvas');
  const W = 1000, H = 700;
  c.width = W; c.height = H;
  const ctx = c.getContext('2d');

  // ── Background gradient ──────────────────────────────────
  const bg = ctx.createLinearGradient(0, 0, W, H);
  bg.addColorStop(0,   '#0d1117');
  bg.addColorStop(0.5, '#161b22');
  bg.addColorStop(1,   '#0d1117');
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, W, H);

  // ── Outer border ─────────────────────────────────────────
  ctx.strokeStyle = '#c9a84c';
  ctx.lineWidth = 6;
  roundRect(ctx, 20, 20, W-40, H-40, 20);
  ctx.stroke();

  // ── Inner border ─────────────────────────────────────────
  ctx.strokeStyle = 'rgba(201,168,76,0.3)';
  ctx.lineWidth = 2;
  roundRect(ctx, 34, 34, W-68, H-68, 14);
  ctx.stroke();

  // ── Corner ornaments ─────────────────────────────────────
  const corners = [[50,50],[W-50,50],[50,H-50],[W-50,H-50]];
  corners.forEach(([x,y]) => {
    ctx.fillStyle = '#c9a84c';
    ctx.font = '28px serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('✦', x, y);
  });

  // ── Bismillah ────────────────────────────────────────────
  ctx.fillStyle = 'rgba(201,168,76,0.6)';
  ctx.font = '22px serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ', W/2, 80);

  // ── Title: CERTIFICATE OF COMPLETION ────────────────────
  ctx.fillStyle = '#c9a84c';
  ctx.font = 'bold 42px "Segoe UI", system-ui, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('CERTIFICATE OF COMPLETION', W/2, 160);

  // ── Decorative line ──────────────────────────────────────
  const grad = ctx.createLinearGradient(100, 0, W-100, 0);
  grad.addColorStop(0,   'transparent');
  grad.addColorStop(0.3, '#c9a84c');
  grad.addColorStop(0.7, '#c9a84c');
  grad.addColorStop(1,   'transparent');
  ctx.strokeStyle = grad;
  ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(100, 190); ctx.lineTo(W-100, 190); ctx.stroke();

  // ── "This certifies that" ────────────────────────────────
  ctx.fillStyle = '#8b949e';
  ctx.font = '20px "Segoe UI", system-ui, sans-serif';
  ctx.fillText('This certifies that', W/2, 230);

  // ── Student name ─────────────────────────────────────────
  ctx.fillStyle = '#e6edf3';
  ctx.font = 'bold 52px "Segoe UI", system-ui, sans-serif';
  ctx.fillText(opts.name || 'Student', W/2, 300);

  // ── "has successfully completed" ─────────────────────────
  ctx.fillStyle = '#8b949e';
  ctx.font = '20px "Segoe UI", system-ui, sans-serif';
  ctx.fillText('has successfully completed the quiz on', W/2, 355);

  // ── World name ───────────────────────────────────────────
  ctx.fillStyle = '#c9a84c';
  ctx.font = 'bold 38px "Segoe UI", system-ui, sans-serif';
  ctx.fillText(opts.worldEmoji + '  ' + opts.worldName, W/2, 415);

  // ── Score ────────────────────────────────────────────────
  ctx.fillStyle = '#3fb950';
  ctx.font = 'bold 28px "Segoe UI", system-ui, sans-serif';
  ctx.fillText('Score: ' + opts.score + '%  ·  ' + opts.total + ' Questions Completed', W/2, 470);

  // ── Decorative line ──────────────────────────────────────
  ctx.strokeStyle = grad;
  ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(100, 510); ctx.lineTo(W-100, 510); ctx.stroke();

  // ── Date & seal ──────────────────────────────────────────
  ctx.fillStyle = '#8b949e';
  ctx.font = '18px "Segoe UI", system-ui, sans-serif';
  ctx.fillText('Date of Completion: ' + opts.date, W/2, 550);

  // ── Seal circle ──────────────────────────────────────────
  ctx.beginPath();
  ctx.arc(W/2, 620, 40, 0, Math.PI*2);
  ctx.strokeStyle = '#c9a84c';
  ctx.lineWidth = 3;
  ctx.stroke();
  ctx.fillStyle = 'rgba(201,168,76,0.1)';
  ctx.fill();
  ctx.fillStyle = '#c9a84c';
  ctx.font = 'bold 28px serif';
  ctx.fillText('✦', W/2, 620);

  // ── Footer ───────────────────────────────────────────────
  ctx.fillStyle = 'rgba(201,168,76,0.4)';
  ctx.font = '14px "Segoe UI", system-ui, sans-serif';
  ctx.fillText('Seerah Quiz · Islamic Knowledge Series', W/2, 670);
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x+r, y);
  ctx.lineTo(x+w-r, y);
  ctx.quadraticCurveTo(x+w, y, x+w, y+r);
  ctx.lineTo(x+w, y+h-r);
  ctx.quadraticCurveTo(x+w, y+h, x+w-r, y+h);
  ctx.lineTo(x+r, y+h);
  ctx.quadraticCurveTo(x, y+h, x, y+h-r);
  ctx.lineTo(x, y+r);
  ctx.quadraticCurveTo(x, y, x+r, y);
  ctx.closePath();
}

function downloadCertificate(canvasId, filename) {
  const c = document.getElementById(canvasId || 'cert-canvas');
  const link = document.createElement('a');
  link.download = filename || 'certificate.png';
  link.href = c.toDataURL('image/png');
  link.click();
}
