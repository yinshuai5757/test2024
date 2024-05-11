INSERT INTO ai.ai_types (ai_type_id,name,attention_text,memo,created_datetime,updated_datetime,deleted_datetime) VALUES
    (1,'所内AI',NULL,'Xwin-LM(local)','2024-03-08 00:00:00',NULL,NULL),
	(2,'所外AI',NULL,'GPT4(internet)','2024-03-08 00:00:00',NULL,NULL);

INSERT INTO ai.waiting_statuses (waiting_status_id,name,memo,created_datetime,updated_datetime,deleted_datetime) VALUES
	(0,'処理待ち',NULL,'2024-03-08 00:00:00',NULL,NULL),
	(1,'処理中',NULL,'2024-03-08 00:00:00',NULL,NULL),
	(9,'処理完了',NULL,'2024-03-08 00:00:00',NULL,NULL),
	(51,'エラー終了（Frontend）',NULL,'2024-03-08 00:00:00',NULL,NULL),
	(52,'エラー終了（Backend）',NULL,'2024-03-08 00:00:00',NULL,NULL),
	(53,'エラー終了（LLM）',NULL,'2024-03-08 00:00:00',NULL,NULL),
	(80,'タイムアウト',NULL,'2024-03-08 00:00:00',NULL,NULL),
	(90,'キャンセル',NULL,'2024-03-08 00:00:00',NULL,NULL);
