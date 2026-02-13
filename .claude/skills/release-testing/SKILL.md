---
name: release-testing
description: Test documentation instructions by working through the page step by step and performing actions using the playwright-cli. Use when the user asks you to test a specific page.
allowed-tools: Bash(playwright-cli:*)
---

# Testing documentation pages

When testing documentation pages you should:

- Build a fresh version of the nightly documentation.
- Locate the page you have been asked to test within the `build` directory (use the `*.html.md` version of the page).
- Read the instructions on the page.
- Check the parent directory for another project called `deployment-internal` as it contains additional instructions.
  - Additional private instructions for using NVIDIA systems are stored in markdown files in this project.
  - If you cannot find this project than ask the user for it's location.
  - Before you start testing a page review any related pages in `deployment-internal`.
- Use the `playwright-cli` tool to drive a browser and follow the instructions (use a headed browser).
- Provide a report to the user, include:
  - Full list of compute resources you created.
  - Any problems you found.

## Goals

- Follow every step of the instructions in the documentation.
- Track any differences between the documentation and the real world experience.
- Verify that RAPIDS is installed successfully.

## Instructions

Most of the instructions focus on creating cloud infrastructure by clicking through GUIs on third-party cloud platforms. Some things to focus on:

- If you need to authenticate ask the user to do this for you.
- If documentation has both GUI and CLI instructions focus on the GUI instructions.
- Wait for compute resources to launch before continuing.
- Buttons and menus may change and move around, if you cannot find the exact thing try and find a way to do the same action, note this difference in your report.
- If a deployment fails or you get an error message ask the user for assistance.
- If you repeat steps over and over without making progress ask the user for help.
- Every page should end with a step that verifies RAPIDS is installed and can be used. If this is missing note it in your report.
- Before performing destructuve actions like deleting a resource always ask the user for confirmation first
