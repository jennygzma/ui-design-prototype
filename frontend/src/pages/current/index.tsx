import { Stack, Typography, Button } from "@mui/material";
import React, { useState } from "react";
import UserInputs from "./components/user-inputs";
import CodeGeneration from "./components/code-generation";
import Plan from "./components/plan";
import { PlanProvider, usePlanContext } from "./hooks/plan-context";

// This prototype focuses on planning and getting a fully planned out version with the code ready
const Home = () => {

  return (
    <div className={"home"}>
      <Stack spacing="20px" sx={{ padding: "20px" }}>
        <Stack
          direction="row"
          spacing="20px"
          sx={{
            alignItems: "flex-start",
            alignContent: "flex-end",
            justifyContent: "center",
          }}
        >
          <img
            src={require("../../assets/franky-icon.ico")}
            alt="chopper"
            width="150x"
          />
          <Typography variant="h1" sx={{ alignSelf: "center" }}>
            UX Prototype
          </Typography>
        </Stack>
        <PlanProvider>
          <UserInputs />
          <Plan/>
          <CodeGeneration />
        </PlanProvider>
      </Stack>
    </div>
  );
};

export default Home;
