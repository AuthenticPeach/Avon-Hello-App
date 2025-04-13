# Avon Hello - Customer Order Manager

Avon Hello is a lightweight desktop application for managing Avon customer orders. It allows you to add and edit customer details, track orders, generate professional invoices, and export them as PDFs.

---

## ✅ Features

- Add/edit/delete customer info (including office & cell phone numbers)
- Create and manage detailed customer orders
- Built-in order history tracking
- Custom processing charges, tax, and discounts per item
- Professional invoice export to PDF
- Auto-formatted phone numbers
- Uses your default Downloads folder for saving invoices
- Installer with desktop shortcut and taskbar icon

---

## 📦 Installation

### 📁 Step 1: Download the Installer

Download the latest version of the **Avon Hello Installer** (`avon-hello.exe`) from your provided source (e.g. USB, cloud storage, or email).

---

### 🚀 Step 2: Run the Installer

1. Double-click `avon-hello.exe`
2. Follow the prompts. The installer will:
   - Create a shortcut on your desktop
   - Add the app to your Windows Start Menu

> ⚠️ You may get a SmartScreen or antivirus prompt. Click **More Info → Run Anyway** (this is normal for custom apps not yet signed by Microsoft).

---

## 📂 File Placement & Usage Notes

- The app stores data in a file named `avon_hello.db` (automatically created on first use).
- All **invoice PDFs** are saved in your **Downloads folder**.
- App settings (e.g. dark mode, campaign number) are stored in `settings.conf`.

---

## 📤 Exported PDFs

- Exported invoices are saved in your **Downloads** folder
- Filename format:  
  `invoice-[customername]-[YYYY-MM-DD].pdf`
- Phone numbers are auto-formatted for clarity
- Discounts and shades/fragrances are included in product details
- Only selected charges (tax/processing) appear based on checkbox settings

---

## 🛠️ Troubleshooting

- ❌ **App won’t open or crashes immediately**  
  ➤ Right-click the shortcut → Run as Administrator  
  ➤ Check for missing files like `avon_hello.db` in the app directory

- ❌ **"No such table" errors**  
  ➤ Ensure you've let the app create its database by visiting the **Customers** screen at least once.

---

## 🧼 Resetting the App (Optional)

To start fresh:

1. Delete the `avon_hello.db` file from the app directory
2. Restart the app to recreate a fresh database

---

## 💼 Credits

App designed by **AuthenticPeach**  
Built with Python + Qt5  
Packaged using PyInstaller  
