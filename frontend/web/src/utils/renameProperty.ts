import { ArboristNodeType, JSCNodeType } from "@/app/page";

type JSCNodeWithIdType = {
  id: string;
  node_name: string;
  sample_format: string;
  user_format: string;
  sample_generated_text: string;
  sort_order: number;
  children: any;
};

export const convertToJSCProperty = (
  nodes: ArboristNodeType[]
): JSCNodeType[] => {
  return nodes.map((node) => {
    const { name, id, ...rest } = node;
    return {
      ...rest,
      node_name: name,
      children: convertToJSCProperty(node.children),
    };
  });
};

let uniqueId = 1;

export const convertToArboristProperty = (
  nodes: JSCNodeType[],
  parentId: string = ""
): ArboristNodeType[] => {
  return nodes.map((node) => {
    const { node_name, ...rest } = node;
    const id = parentId ? `${parentId}-${uniqueId}` : `${uniqueId}`;
    uniqueId++;
    return {
      ...rest,
      id,
      name: node_name,
      children: convertToArboristProperty(node.children),
    };
  });
};
