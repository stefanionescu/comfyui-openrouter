const aliasMessage = 'Export the source value directly instead of adding an exported const alias.';

function unwrapExpression(node) {
  let current = node;
  while (
    current?.type === 'ChainExpression' ||
    current?.type === 'TSAsExpression' ||
    current?.type === 'TSSatisfiesExpression' ||
    current?.type === 'TSNonNullExpression'
  ) {
    current = current.expression;
  }
  return current;
}

function isIdentifierMemberExpression(node) {
  const current = unwrapExpression(node);
  if (!current) {
    return false;
  }
  if (current.type === 'Identifier') {
    return true;
  }
  if (current.type !== 'MemberExpression') {
    return false;
  }
  return isIdentifierMemberExpression(current.object);
}

function exportedDeclarations(sourceCode, node) {
  const declarations = [];
  if (node.declaration?.type === 'VariableDeclaration' && node.declaration.kind === 'const') {
    declarations.push(...node.declaration.declarations);
  }
  if (node.source) return declarations;
  const scope = sourceCode.getScope(node);
  for (const specifier of node.specifiers) {
    const variable = scope.set.get(specifier.local.name);
    declarations.push(...constantDeclarations(variable));
  }
  return declarations;
}

function constantDeclarations(variable) {
  const declarations = [];
  for (const definition of variable?.defs ?? []) {
    if (definition.type === 'Variable' && definition.parent.kind === 'const') {
      declarations.push(definition.node);
    }
  }
  return declarations;
}

export const noExportedAliasConstants = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow exported const aliases that only rename another identifier/member.',
    },
    schema: [],
  },
  create(context) {
    const sourceCode = context.sourceCode;
    const report = context.report.bind(context);
    return {
      ExportNamedDeclaration(node) {
        for (const declarator of exportedDeclarations(sourceCode, node)) {
          if (!isIdentifierMemberExpression(declarator.init)) {
            continue;
          }

          report({
            node: declarator,
            message: aliasMessage,
          });
        }
      },
    };
  },
};
