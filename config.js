// Clause configuration. In this static stack this module stands in for build-time values.
export const CONTRACT = "0x7a7Cf4eaD9e577e2061628e348A6b16524dA8AA4";
export const NETWORK = "studionet";
export const CHAIN_ID = "0xf22f";
export const EXPLAINER_DOC = "https://docs.genlayer.com/";
// Demo mode is on only when no valid contract address is configured. It never
// pretends to be a real on-chain interaction.
export const DEMO = !/^0x[0-9a-fA-F]{40}$/.test(CONTRACT);
