type Template = {
  id: string;
  name: string;
  ai_type_ids: number[];
  sample_case_memo: string;
  template_tree: string;
};

const templateData: Template = {
  id: "root",
  name: "Sample Template",
  ai_type_ids: [1, 2, 3],
  sample_case_memo: "Example memo",
  template_tree: JSON.stringify([
    {
      node_name: "Node 1",
      sample_format: "Format 1",
      sample_generated_text: "Generated text 1",
      children: [
        {
          node_name: "Node 1-1",
          sample_format: "Format 1-1",
          sample_generated_text: "Generated text 1-1",
        },
      ],
    },
  ]),
};
