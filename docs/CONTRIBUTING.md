# 🙌 Contributing to realloc

First, thank you for considering contributing to `realloc`!  
Your help makes this project better for everyone.

This document outlines the process for contributing fixes, features, and improvements.

---

## ✨ Code of Conduct

We expect contributors to behave respectfully and professionally.  
This is an open, inclusive community — everyone is welcome.

---

## 📚 Before You Start

- Please read [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md) to understand the architecture and philosophy.
- Check [API_REFERENCE.md](API_REFERENCE.md) to see existing classes and methods.
- Review open issues or propose a new one if needed.

---

## 🛠 How to Contribute

### 1. Fork the Repository

Click "Fork" on GitHub to create your own copy of the project.

---

### 2. Clone Your Fork Locally

```bash
git clone https://github.com/your-username/realloc.git
cd realloc
```

### 3. Create a New Branch
Name your branch descriptively:

`git checkout -b feature/my-new-feature`

Examples:
* feature/tax-loss-harvesting
* fix/cash-allocation-rounding
* docs/update-api-reference

### 4. Install Dependencies
Make sure you install dev tools:

`pip install -e .[dev]`

### 5. Run Tests
Make sure all tests pass:

`make test`

### 6. Make Your Changes
* Follow existing code style (PEP8, black formatting)
* Add or update tests if appropriate
* Update examples if needed

### 7. Commit Your Changes
Write clear, descriptive commit messages:

`git commit -m "Add support for tax loss harvesting in rebalance"`

### 8. Push and Open a Pull Request
`git push origin feature/my-new-feature`

Then open a Pull Request against the main branch on GitHub.

✅ Describe what you changed and why
✅ Reference any related issues

### 🧪 Test Guidelines

* All new features must include at least one test.
* Tests should be written using pytest.
* Aim for high coverage, especially around critical logic (TradeAccountMatrix, PortfolioAllocator, selectors).

### 💬 Need Help?

Feel free to open a discussion or GitHub Issue if you:

* Want feedback before starting a big change
* Find a tricky bug and aren't sure about fixing it
* Have a question about the architecture 

We're happy to help!

🚀 Thank You!

We appreciate your interest and effort — together we can make realloc a world-class portfolio management toolkit.