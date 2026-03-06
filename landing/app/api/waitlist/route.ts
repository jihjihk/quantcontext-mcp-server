import { Resend } from "resend";
import { NextResponse } from "next/server";

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request: Request) {
  try {
    const { email } = await request.json();

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return NextResponse.json({ error: "Valid email required" }, { status: 400 });
    }

    const audienceId = process.env.RESEND_AUDIENCE_ID;

    if (audienceId) {
      await resend.contacts.create({
        email,
        audienceId,
      });
    } else {
      // Fallback: send notification email to team
      await resend.emails.send({
        from: "QuantContext <waitlist@quantcontext.ai>",
        to: "jihyun@zommalabs.com",
        subject: `Waitlist signup: ${email}`,
        text: `New waitlist signup: ${email}`,
      });
    }

    return NextResponse.json({ success: true });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : "Unknown error";
    console.error("Waitlist error:", message);
    return NextResponse.json({ error: "Failed to join waitlist" }, { status: 500 });
  }
}
