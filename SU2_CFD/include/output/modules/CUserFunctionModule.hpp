#pragma once

#include "COutputModule.hpp"

class CUserFunctionModule final : public CSolverOutputModule {

  using FieldRef = typename COutFieldCollection::Map::iterator;
  using FieldRefFuncPair  = std::pair<FieldRef, interpreter::UserFunction*>;
  using FieldRefTokenPair = std::pair<FieldRef, packToken*>;

  TokenMap historyScope;
  TokenMap volumeScope;

  std::vector<interpreter::UserFunction*> historyUserFunctions;
  std::vector<interpreter::UserFunction*> volumeUserFunctions;
  std::vector<string> inlineHistoryUserFunctions;
  std::vector<string> inlineVolumeUserFunctions;

  std::vector<FieldRefTokenPair> histFieldTokenRefs;
  std::vector<FieldRefTokenPair> volFieldTokenRefs;

  std::vector<FieldRefFuncPair> funcHistFieldRefs;
  std::vector<FieldRefFuncPair>  funcVolFieldRefs;

public:
  explicit CUserFunctionModule(CConfig *config, int nDim);

  void DefineHistoryFieldModifier(CHistoryOutFieldManager& historyFields) override;

  void LoadHistoryDataModifier(CHistoryOutFieldManager& historyFields) override;

  void DefineHistoryFields(CHistoryOutFieldManager& historyFields) override;

  void DefineVolumeFields(CVolumeOutFieldManager& volumeFields) override;

  void LoadSurfaceData(CVolumeOutFieldManager& volumeFields) override;

  void LoadVolumeData(CVolumeOutFieldManager& volumeFields) override;

  std::string GetName(const std::string& baseName);

  void EvalUserFunctions(const std::vector<FieldRefTokenPair> &fieldTokenRef,
                         const std::vector<FieldRefFuncPair> &funcFieldRef, TokenMap &scope);
};

