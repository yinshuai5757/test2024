"use client";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

import { Header } from "@/components/base/header";
import { FormatArea } from "@/components/base/format-area";
import {
  TooltipProvider,
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@radix-ui/react-tooltip";
import { useEffect, useState } from "react";
import { Progress } from "@/components/ui/progress";
import { TooltipDialog } from "@/components/base/tooltip-dialog";
import { TreeView } from "@/components/base/tree-view";
import { CaseMemoArea } from "@/components/base/case-memo-area";
import { GeneratedArea } from "@/components/base/generated-area";
import { TrashSvg } from "@/data/image/trash-svg";
import { DownloadSvg } from "@/data/image/download-svg";
import fetchData from "@/utils/fetchData";
import { convertToArboristProperty } from "@/utils/renameProperty";
import { SERVER_BASE_URL } from "@/const/const";

type TemplatesType = {
  template_id: number;
  name: string;
}[];

type AiTypesType = {
  ai_type_id: number;
  name: string;
};

export type ArboristNodeType = {
  id: string;
  name: string;
  sample_format: string;
  user_format: string;
  sample_generated_text: string;
  sort_order: number;
  children: any;
};

export type JSCNodeType = {
  node_name: string;
  sample_format: string;
  user_format: string;
  sample_generated_text: string;
  sort_order: number;
  children: any;
};

type ArboristTemplateType = {
  template_id: number;
  name: string;
  sample_case_memo: string;
  user_case_memo: string;
  template_tree: ArboristNodeType[] | [];
};

type JSCTemplateType = {
  template_id: number;
  name: string;
  sample_case_memo: string;
  user_case_memo: string;
  template_tree: JSCNodeType[] | [];
}[];

export default function Home() {
  // 共通
  const [isBtnDisabled, setIsBtnDisabled] = useState(true);
  const [loading, setLoading] = useState(true);

  // テンプレート 関連
  const [templates, setTemplates] = useState<TemplatesType>([]);
  const [templateId, setTemplateId] = useState(0);

  const handleTemplate = async (value: string) => {
    setTemplateId(Number(value));
    setIsAiTypeEnabled(true);
  };

  // AIの種類 関連
  const [isAiTypeEnabled, setIsAiTypeEnabled] = useState(false);
  const [aiTypes, setAiTypes] = useState<AiTypesType[]>([]);

  // 文章の生成処理 関連
  const [alertDialogName, setAlertDialogName] = useState<
    "agree" | "progress" | "suspend" | "complete" | ""
  >("");
  const [progress, setProgress] = useState(0);

  // ツリービュー 関連
  const [data, setData] = useState<ArboristTemplateType | null>(null);

  useEffect(() => {
    const urls = [
      `${SERVER_BASE_URL}/api/jsc/templates`,
      `${SERVER_BASE_URL}/api/jsc/ai_types`,
    ];

    Promise.all([
      fetchData<TemplatesType>(urls[0]),
      fetchData<AiTypesType[]>(urls[1]),
    ])
      .then((results) => {
        if (results[0] === null || results[1] === null) {
          throw new Error("Failed to fetch data");
        }
        console.log(results);
        const [templates, aiTypes] = results;
        setTemplates(templates);
        setAiTypes(aiTypes);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const template = await fetch(
          `${SERVER_BASE_URL}/api/jsc/templates/${templateId}`
        ).then((res) => {
          return res.json();
        });
        setData({
          ...template[0],
          template_tree: convertToArboristProperty(template[0].template_tree),
        });
      } catch (error) {
        console.error("Error fetching template data:", error);
      } finally {
        setLoading(false);
      }
    };
    if (templateId !== 0) {
      fetchData();
    }
  }, [templateId]);

  const [selectedNodeData, setSelectedNodeData] = useState<ArboristNodeType>({
    id: "",
    name: "",
    sample_format: "",
    user_format: "",
    sample_generated_text: "",
    sort_order: 0,
    children: [],
  });
  const [caseMemo, setCaseMemo] = useState(
    data
      ? data.user_case_memo
        ? data.user_case_memo
        : data.sample_case_memo
      : ""
  );

  const handleSelect = (nodeData: ArboristNodeType) => {
    setSelectedNodeData({ ...nodeData });
  };

  return (
    <div className="flex h-screen flex-col">
      {/* NOTE: textareaの高さが動的に変わる際にfooterだけを固定にするため、
      headerとmainを囲んだエリアにflex-growとoverflowを適用している */}
      <div className="flex grow flex-col overflow-auto">
        <Header />
        <main className="flex grow flex-col space-y-4 bg-[#EFEEE9] p-4">
          <div className="flex items-center space-x-2">
            <div className="flex grow">
              <Label
                htmlFor="claim_type"
                className="bg-brand flex w-32 items-center justify-center rounded-l-3xl text-white"
              >
                書面の種類
              </Label>
              <Select
                onValueChange={(value) => {
                  handleTemplate(value);
                }}
              >
                <SelectTrigger className="rounded-l-none bg-white">
                  <SelectValue placeholder="テンプレートを選択する" />
                </SelectTrigger>
                {templates && templates.length !== 0 && (
                  <SelectContent>
                    {templates.map((template) => (
                      <SelectItem
                        key={template.template_id}
                        value={String(template.template_id)}
                      >
                        {template.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                )}
              </Select>
            </div>
            <Select disabled={!isAiTypeEnabled}>
              <SelectTrigger
                className={`h-10 w-48 ${
                  isAiTypeEnabled ? "bg-white" : "bg-disabled"
                }`}
              >
                <SelectValue placeholder="利用モデルを選択" />
              </SelectTrigger>
              {aiTypes && aiTypes.length !== 0 && (
                <SelectContent>
                  {aiTypes.map((aiType: AiTypesType) => (
                    <SelectItem
                      key={aiType.ai_type_id}
                      value={String(aiType?.ai_type_id)}
                    >
                      {aiType?.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              )}
            </Select>
            <TooltipDialog title="書面の構成について">
              <div>
                <ul className="list-disc space-y-4 pl-5">
                  <li className="space-y-1">
                    <h3 className="font-bold">条項の選択</h3>
                    <div className="text-sm">
                      <p>
                        条項を選択すると生成される文章のサンプル「書面として生成される内容」と「AIへの指示内容」が表示されます。
                      </p>
                      <p>これらは編集することができます。</p>
                    </div>
                  </li>
                  <li className="space-y-1">
                    <h3 className="font-bold">条項の移動</h3>
                    <div className="text-sm">
                      <p>
                        条項をドラッグすることで条項の順番や階層を移動できます。
                      </p>
                    </div>
                  </li>
                  <li className="space-y-1">
                    <h3 className="font-bold">チェックボックス</h3>
                    <div className="text-sm">
                      <p>
                        チェックボックスで選択した条項の文章をAIで生成します。
                      </p>
                      <p>
                        またバケツアイコン
                        <span className="bg-inactive px-1">
                          <TrashSvg className="svg-gray inline-block size-3" />
                        </span>
                        をクリックすることで選択した条項を削除できます。
                      </p>
                    </div>
                  </li>
                </ul>
              </div>
            </TooltipDialog>
          </div>
          <div className="grid grow grid-cols-5 gap-4">
            <div className="col-span-2 flex flex-col bg-white">
              <div className="bg-inactive flex items-center justify-between pl-2">
                <h2 className="font-bold">書面の構成</h2>
                <TooltipDialog title="書面の構成について">
                  <div>
                    <ul className="list-disc space-y-4 pl-5">
                      <li className="space-y-1">
                        <h3 className="font-bold">条項の選択</h3>
                        <div className="text-sm">
                          <p>
                            条項を選択すると生成される文章のサンプル「書面として生成される内容」と「AIへの指示内容」が表示されます。
                          </p>
                          <p>これらは編集することができます。</p>
                        </div>
                      </li>
                      <li className="space-y-1">
                        <h3 className="font-bold">条項の移動</h3>
                        <div className="text-sm">
                          <p>
                            条項をドラッグすることで条項の順番や階層を移動できます。
                          </p>
                        </div>
                      </li>
                      <li className="space-y-1">
                        <h3 className="font-bold">チェックボックス</h3>
                        <div className="text-sm">
                          <p>
                            チェックボックスで選択した条項の文章をAIで生成します。
                          </p>
                          <p>
                            またバケツアイコン
                            <span className="bg-inactive px-1">
                              <TrashSvg className="svg-gray inline-block size-3" />
                            </span>
                            をクリックすることで選択した条項を削除できます。
                          </p>
                        </div>
                      </li>
                    </ul>
                  </div>
                </TooltipDialog>
              </div>
              {/* <TreeNodeList /> */}
              {data && (
                <TreeView
                  data={data.template_tree}
                  loading={loading}
                  templateId={templateId}
                  onSelect={handleSelect}
                />
              )}
            </div>
            <div className="col-span-3 flex flex-col space-y-4">
              <CaseMemoArea
                title="ヒアリング項目（ケースメモ）"
                userCaseMemo={data?.user_case_memo || ""}
                sampleCaseMemo={data?.sample_case_memo || ""}
                onUserTextChange={(text: string) => setCaseMemo(text)}
              />
              <FormatArea
                title="AIへの指示内容"
                userText={selectedNodeData?.sample_format || ""}
                sampleText={selectedNodeData?.user_format || ""}
                onUserTextChange={(text: string) =>
                  setSelectedNodeData({
                    ...selectedNodeData,
                    user_format: text,
                  })
                }
              />
              <GeneratedArea
                title="書面として生成される内容"
                userGeneratedText={
                  selectedNodeData?.sample_generated_text || ""
                }
                sampleGeneratedText={
                  selectedNodeData?.sample_generated_text || ""
                }
                onUserTextChange={(text: string) =>
                  setSelectedNodeData({
                    ...selectedNodeData,
                    sample_generated_text: text,
                  })
                }
              />
            </div>
          </div>
        </main>
      </div>
      <footer className="mt-auto">
        <div className="p-2">
          <div className="flex items-end justify-between">
            <p className="text-sm">
              Copyright © Verybest Co., Ltd. All Rights Reserved.
            </p>
            <div className="flex space-x-1">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger
                    asChild
                    onClick={() => {
                      console.log("download");
                    }}
                  >
                    <Button
                      className={`${
                        isBtnDisabled
                          ? "bg-disabled text-white"
                          : "bg-brand hover:bg-brand text-white hover:opacity-70"
                      }`}
                      disabled={isBtnDisabled ? true : false}
                    >
                      <DownloadSvg />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="mb-2 border border-gray-300 bg-white p-1 text-xs">
                      Wordファイルのダウンロード
                    </p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
              <Button className="bg-disabled text-white" disabled>
                テンプレートの保存
              </Button>
              <AlertDialog open={alertDialogName === "agree"}>
                <AlertDialogTrigger asChild>
                  <Button
                    className={`${
                      templateId === 0
                        ? "bg-disabled text-white"
                        : "bg-brand hover:bg-brand text-white hover:opacity-70"
                    }`}
                    disabled={templateId === 0 ? true : false}
                    onClick={() => setAlertDialogName("agree")}
                  >
                    文章の生成
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogDescription className="text-center text-xl">
                      <p>外部のAIが選択されています。</p>
                      <p>
                        <span className="text-red-500">個人情報</span>や
                        <span className="text-red-500">機密情報</span>
                        はありませんか？
                      </p>
                      <p>顧客の同意を得ていますか？</p>
                      <p>問題がある場合は所内AIを選択してください。</p>
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <Separator />
                  <AlertDialogFooter className="flex justify-center space-x-10">
                    <AlertDialogAction
                      className="min-w-24"
                      onClick={() => {
                        // 擬似的にプログレスバーの動きを再現
                        setAlertDialogName("progress");
                        let progress = 0;

                        const interval = setInterval(() => {
                          progress += 20;
                          setProgress(progress);

                          const fetchData = async () => {
                            if (progress === 80) {
                              try {
                                const response = await fetch(
                                  `${SERVER_BASE_URL}/api/jsc/documents`,
                                  {
                                    method: "POST",
                                    headers: {
                                      "Content-Type": "application/json",
                                    },
                                    body: JSON.stringify({}),
                                  }
                                );

                                if (!response.ok) {
                                  throw new Error(
                                    "Network response was not ok"
                                  );
                                }

                                const data = await response.json();
                              } catch (error) {
                                console.error("Error fetching data:", error);
                              }
                            }
                          };

                          if (progress === 80) {
                            fetchData();
                          }

                          if (progress >= 100) {
                            clearInterval(interval);
                            setAlertDialogName("complete");
                          }
                        }, 1000);

                        return () => clearInterval(interval);
                      }}
                    >
                      はい
                    </AlertDialogAction>
                    <AlertDialogCancel
                      className="min-w-24"
                      onClick={() => setAlertDialogName("")}
                    >
                      いいえ
                    </AlertDialogCancel>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
              <AlertDialog open={alertDialogName === "progress"}>
                <AlertDialogContent className="border-0 pt-0">
                  <AlertDialogHeader>
                    <AlertDialogDescription className="bg-brand py-1 text-center text-white">
                      <p>
                        現在AI利用サーバーの利用待ちです。恐れ入りますがもうしばらくお待ちください。
                      </p>
                    </AlertDialogDescription>
                    <div className="flex flex-col space-y-6 p-8">
                      <div className="flex items-center space-x-3">
                        <p className="w-40">利用者待ち状況</p>
                        <Progress
                          value={progress + 20}
                          className="relative h-4 w-full  overflow-hidden rounded-full bg-[#D4DCF6]"
                        />
                      </div>
                      <div className="flex items-center space-x-3">
                        <p
                          className="w-40"
                          onClick={() => setAlertDialogName("complete")}
                        >
                          お客様の処理状況
                        </p>
                        <Progress
                          value={progress}
                          className="relative h-4  overflow-hidden rounded-full bg-[#D4DCF6]"
                        />
                      </div>
                    </div>
                  </AlertDialogHeader>
                  <Separator />
                  <AlertDialogFooter className="flex justify-end space-x-10">
                    <AlertDialogCancel
                      className="bg-brand hover:bg-brand min-w-24 text-white hover:opacity-70"
                      onClick={() => setAlertDialogName("suspend")}
                    >
                      文章生成を中止
                    </AlertDialogCancel>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
              <AlertDialog open={alertDialogName === "suspend"}>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogDescription className="text-center text-xl">
                      <p className="text-red-500">文章の生成を中止しました。</p>
                      <p className="text-red-500">
                        「原告の経歴」まで生成しました。
                      </p>
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <Separator />
                  <AlertDialogFooter className="flex justify-center space-x-10">
                    <AlertDialogAction
                      className="min-w-24"
                      onClick={() => setAlertDialogName("")}
                    >
                      はい
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
              <AlertDialog open={alertDialogName === "complete"}>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogDescription className="text-center text-xl">
                      <span className="text-red-500">
                        文章の生成が完了しました。
                      </span>
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <Separator />
                  <AlertDialogFooter className="flex justify-center space-x-10">
                    <AlertDialogAction
                      className="min-w-24"
                      onClick={() => {
                        setAlertDialogName("");
                        setIsBtnDisabled(false);
                      }}
                    >
                      はい
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
