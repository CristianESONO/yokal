import { SiteHeader } from "@/components/SiteHeader";
import { Hero } from "@/components/Hero";
import { Partners } from "@/components/Partners";
import { Features } from "@/components/Features";
import { Notifications } from "@/components/Notifications";
import { HowItWorks } from "@/components/HowItWorks";
import { Pricing2 } from "@/components/pricing2";
import { Cta } from "@/components/Cta";
import { Footer } from "@/components/footer";

export default function Home() {
  return (
    <div className="flex flex-1 flex-col">
      <SiteHeader />
      <Hero />
      <Partners />
      <main>
        <Features />
        <Notifications />
        <HowItWorks />
        <Pricing2 />
      </main>
      <Cta />
      <Footer />
    </div>
  );
}
