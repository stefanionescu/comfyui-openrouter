/** Node classes whose controls change with the selected option, and the inputs that drive them. */
export const dynamicControlInputs: ReadonlyMap<string, readonly string[]> = new Map([
  [
    'OpenRouterChatAsk',
    [
      'temperature',
      'top_p',
      'top_k',
      'min_p',
      'top_a',
      'frequency_penalty',
      'presence_penalty',
      'repetition_penalty',
    ],
  ],
  ['OpenRouterDecisionAddQuestion', ['answer_type']],
]);
