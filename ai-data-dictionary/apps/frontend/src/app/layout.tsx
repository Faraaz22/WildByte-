import { Inter } from "next/font/google";
import "../styles/globals.css";
import AuthLayout from "../components/common/AuthLayout";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata = {
  title: "AI Data Dictionary",
  description: "Explore tables, schemas, and lineage",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans">
        <AuthLayout>{children}</AuthLayout>
      </body>
    </html>
  );
}
