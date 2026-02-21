import { Inter } from "next/font/google";
import "../styles/globals.css";
import Header from "../components/common/Header";
import Sidebar from "../components/common/Sidebar";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata = {
  title: "AI Data Dictionary",
  description: "Explore tables, schemas, and lineage",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans">
        <div className="app-container">
          <Sidebar />
          <div className="flex-1 flex flex-col">
            <Header />
            <main className="p-6 overflow-auto">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
