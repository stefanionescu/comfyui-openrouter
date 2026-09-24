const message =
  'Inline trivial call-through functions unless they own policy, validation, telemetry, caching, or error handling.';
const unwrapNodeTypes = new Set([
  'AwaitExpression',
  'ChainExpression',
  'TSAsExpression',
  'TSSatisfiesExpression',
  'TSNonNullExpression',
  'TSInstantiationExpression',
]);

function unwrapExpression(node) {
  let current = node;
  while (current && unwrapNodeTypes.has(current.type)) {
    current = current.type === 'AwaitExpression' ? current.argument : current.expression;
  }
  return current;
}

function getStatementExpression(statement) {
  if (statement.type === 'ReturnStatement') {
    return statement.argument;
  }
  if (statement.type === 'ExpressionStatement') {
    return statement.expression;
  }
  return null;
}

function getOnlyCall(body) {
  if (body.type === 'BlockStatement' && body.body.length !== 1) {
    return null;
  }
  const expression = unwrapExpression(
    body.type === 'BlockStatement' ? getStatementExpression(body.body[0]) : body,
  );
  return expression?.type === 'CallExpression' ? expression : null;
}

function getParameterName(parameter) {
  const current = unwrapExpression(parameter);
  if (current?.type === 'Identifier') {
    return current.name;
  }
  if (current?.type === 'AssignmentPattern' && current.left.type === 'Identifier') {
    return current.left.name;
  }
  return null;
}

function getArgumentName(argument) {
  const current = unwrapExpression(argument);
  if (current?.type !== 'Identifier') {
    return null;
  }
  return current.name;
}

function isDirectCallThrough(node, call) {
  const parameterNames = node.params.map(getParameterName);
  if (parameterNames.includes(null)) {
    return false;
  }

  const callee = unwrapExpression(call.callee);
  if (callee?.type !== 'Identifier' || call.arguments.length !== parameterNames.length) {
    return false;
  }
  for (const [index, argument] of call.arguments.entries()) {
    if (getArgumentName(argument) !== parameterNames.at(index)) return false;
  }
  return true;
}

function isAllowed(context, functionName, allow) {
  if (!functionName || allow.length === 0) {
    return false;
  }

  const filename = context.physicalFilename.replaceAll('\\', '/');
  const key = `${filename}:${functionName}`;
  for (const entry of allow) {
    if (key === entry || key.endsWith(`/${entry}`)) return true;
  }
  return false;
}

function reportCallThrough(context, allow, node) {
  const functionName =
    node.id?.name ?? (node.parent.type === 'VariableDeclarator' ? node.parent.id.name : null);
  if (!functionName || isAllowed(context, functionName, allow)) {
    return;
  }

  const call = getOnlyCall(node.body);
  if (call && isDirectCallThrough(node, call)) {
    context.report({ node, message: message });
  }
}

export const noCallThrough = {
  meta: {
    type: 'problem',
    docs: {
      description:
        'Disallow trivial functions whose only behavior is forwarding their parameters to another call.',
    },
    schema: [
      {
        type: 'object',
        properties: {
          allow: {
            type: 'array',
            items: { type: 'string' },
          },
        },
        additionalProperties: false,
      },
    ],
  },
  create(context) {
    const allow = context.options[0]?.allow ?? [];
    const visit = reportCallThrough.bind(null, context, allow);
    return {
      FunctionDeclaration: visit,
      FunctionExpression: visit,
      ArrowFunctionExpression: visit,
    };
  },
};
