// Observable Framework refuses to build over an existing output directory, so clear it first.
import {rmSync} from "node:fs";
rmSync(new URL("../docs/dashboard", import.meta.url), {recursive: true, force: true});
