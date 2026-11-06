// Parse static React Router declarations without importing or running app code.
// Parent paths and pathless layouts: https://reactrouter.com/start/declarative/routing
import { createRequire } from "node:module";
import { join } from "node:path";

export function routeParser(repo) {
  let ts;
  try { ts = createRequire(join(repo, "package.json"))("typescript"); }
  catch { return null; }
  return (source, file) => {
    const tree = ts.createSourceFile(file, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
    const routes = [], variables = new Map();
    const routeNames = new Set(["Route"]);
    function text(node) { return node ? node.getText(tree) : ""; }
    function literal(node) {
      if (!node) return null;
      if (ts.isJsxExpression(node)) node = node.expression;
      return node && (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) ? node.text : null;
    }
    function attrs(node) {
      const values = {};
      for (const attr of node.attributes.properties) {
        if (ts.isJsxAttribute(attr)) values[text(attr.name)] = attr.initializer || true;
      }
      return values;
    }
    function guarded(value) { return /ProtectedRoute|RequireAuth|PrivateRoute|AuthGuard|RequireUser|RequireAdmin/i.test(value); }
    function joined(parent, part) {
      if (!part) return parent || "/";
      return (part.startsWith("/") ? part : `${parent}/${part}`).replace(/\/{2,}/g, "/").replace(/\/$/, "") || "/";
    }
    function add(path, context, reason) {
      const auth = context.auth || /\/(?:login|logout|signin|signup|register|auth)(?:\/|$)/i.test(path);
      const dynamic = /[:*?]/.test(path);
      routes.push({ path, kind: auth ? "auth" : context.unknown ? "candidate" : dynamic ? "dynamic" : "public", source: file,
        reason: auth ? "authentication flow or inherited guard" : context.unknown ? "unresolved parent path or basename; verify the actual URL" : dynamic ? "path needs concrete parameter values" : reason });
    }
    function jsx(node, context = { path: "", auth: false }) {
      if (ts.isJsxElement(node) || ts.isJsxSelfClosingElement(node)) {
        const opening = ts.isJsxElement(node) ? node.openingElement : node;
        const name = text(opening.tagName), values = attrs(opening);
        let next = context;
        if (["BrowserRouter", "HashRouter"].includes(name)) {
          next = { ...context, path: joined(context.path, literal(values.basename) || ""),
            unknown: context.unknown || Boolean(values.basename && literal(values.basename) === null) };
        }
        if (routeNames.has(name)) {
          const raw = literal(values.path);
          const path = joined(context.path, raw || "");
          next = { path, auth: context.auth || guarded(text(values.element)),
            unknown: context.unknown || Boolean(values.path && raw === null) };
          if (raw !== null || values.index) add(path, next, "static JSX route; verify runtime redirects");
        }
        if (ts.isJsxElement(node)) for (const child of node.children) jsx(child, next);
        return;
      }
      ts.forEachChild(node, child => jsx(child, context));
    }
    function unwrapped(node, seen = new Set()) {
      if (!node) return null;
      if (ts.isIdentifier(node) && variables.has(node.text) && !seen.has(node.text)) {
        seen.add(node.text); return unwrapped(variables.get(node.text), seen);
      }
      if (ts.isAsExpression(node) || ts.isSatisfiesExpression(node) || ts.isParenthesizedExpression(node)) return unwrapped(node.expression, seen);
      return node;
    }
    function properties(node) {
      const map = {};
      if (node && ts.isObjectLiteralExpression(node)) for (const property of node.properties) {
        if (ts.isPropertyAssignment(property)) map[text(property.name).replace(/^['"]|['"]$/g, "")] = property.initializer;
      }
      return map;
    }
    function objects(node, context) {
      node = unwrapped(node);
      if (!node || !ts.isArrayLiteralExpression(node)) return;
      for (const element of node.elements) {
        const p = properties(unwrapped(element));
        if (!Object.keys(p).length) continue;
        const raw = literal(p.path), path = joined(context.path, raw || "");
        const next = { path, auth: context.auth || guarded(text(p.element) + " " + text(p.Component)),
          unknown: context.unknown || Boolean(p.path && raw === null) };
        if (raw !== null || p.index?.kind === ts.SyntaxKind.TrueKeyword) add(path, next, "static route object; verify loaders and redirects");
        objects(p.children, next);
      }
    }
    function inventory(node) {
      if (ts.isVariableDeclaration(node) && ts.isIdentifier(node.name)) variables.set(node.name.text, node.initializer);
      if (ts.isImportDeclaration(node) && /react-router/.test(literal(node.moduleSpecifier) || "")) {
        const bindings = node.importClause?.namedBindings;
        if (bindings && ts.isNamedImports(bindings)) for (const item of bindings.elements) {
          if ((item.propertyName?.text || item.name.text) === "Route") routeNames.add(item.name.text);
        }
      }
      ts.forEachChild(node, inventory);
    }
    inventory(tree);
    jsx(tree);
    function dataRoutes(node) {
      if (ts.isCallExpression(node) && /^(?:createBrowserRouter|createHashRouter|useRoutes)$/.test(text(node.expression))) {
        const options = properties(node.arguments[1]);
        objects(node.arguments[0], { path: literal(options.basename) || "", auth: false,
          unknown: Boolean(options.basename && literal(options.basename) === null) });
      }
      ts.forEachChild(node, dataRoutes);
    }
    dataRoutes(tree);
    return routes;
  };
}
