#!/usr/bin/env node
import { spawn } from "node:child_process";
import { readFile } from "node:fs/promises";

const allowedCommands = new Set(["buildable", "affected", "full", "smoke", "health"]);

export async function loadCommand(name, configurationUrl = new URL("./commands.json", import.meta.url)) {
  if (!allowedCommands.has(name)) throw new Error("unsupported delivery command");
  const parsed = JSON.parse(await readFile(configurationUrl, "utf8"));
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new Error("invalid delivery command configuration");
  }
  const command = parsed[name];
  if (
    !Array.isArray(command) ||
    command.length === 0 ||
    !command.every((item) => typeof item === "string" && item.length > 0)
  ) {
    throw new Error("invalid delivery command configuration");
  }
  return command;
}

/**
 * Resolve the install command from the repository manifest. A delivery command
 * that runs against whatever happens to be on the machine is not reproducible:
 * without an install a missing node_modules silently falls through to an
 * unrelated global tool, so the result depends on the host rather than the
 * commit. Installs are lockfile-pinned so they cannot drift either.
 */
export async function installCommand(root) {
  let manifest;
  try {
    manifest = JSON.parse(await readFile(new URL("package.json", root), "utf8"));
  } catch {
    return undefined;
  }
  const declared = typeof manifest.packageManager === "string" ? manifest.packageManager : "";
  const name = declared.split("@")[0];
  if (name === "pnpm") return ["pnpm", "install", "--frozen-lockfile"];
  if (name === "yarn") return ["yarn", "install", "--immutable"];
  return ["npm", "ci"];
}

function spawnCommand([executable, ...args], root) {
  const child = spawn(executable, args, {
    cwd: root,
    env: process.env,
    shell: false,
    stdio: "inherit",
  });
  return new Promise((resolve, reject) => {
    child.once("error", reject);
    child.once("exit", (code, signal) => {
      if (signal !== null) reject(new Error("delivery command terminated by signal"));
      else resolve(code ?? 1);
    });
  });
}

export async function run(name) {
  const root = new URL("../", import.meta.url);
  // Neither read depends on the other, so they are not made to wait in turn.
  const [command, install] = await Promise.all([loadCommand(name), installCommand(root)]);
  if (install !== undefined) {
    const installed = await spawnCommand(install, root);
    if (installed !== 0) return installed;
  }
  return spawnCommand(command, root);
}

if (process.argv[1] !== undefined && import.meta.url === new URL(process.argv[1], "file:").href) {
  try {
    process.exitCode = await run(process.argv[2]);
  } catch {
    console.error("delivery command failed");
    process.exitCode = 1;
  }
}
