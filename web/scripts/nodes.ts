/** Node classes whose controls change with the selected option, and the inputs that drive them. */
export const dynamicControlInputs: ReadonlyMap<string, readonly string[]> = new Map([
  ['OpenRouterChatAsk', ['model']],
  ['OpenRouterImageGenerate', ['model']],
  ['OpenRouterVideoGenerate', ['model']],
  ['OpenRouterAudioSpeak', ['model']],
  ['OpenRouterAudioTranscribe', ['model']],
  ['OpenRouterSearchEmbed', ['model']],
  ['OpenRouterSearchRank', ['model']],
  ['OpenRouterDecisionAsk', ['model']],
  ['OpenRouterDecisionAddQuestion', ['answer_type']],
]);
