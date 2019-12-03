
// ----------------------------------------------------
// Team Number to Meta Team and Robot Number mappings
// MEAM510
// ----------------------------------------------------

#include "robotNumToMetaTeam.h"


// index of array is the team number, team2meta[idx] = meta team number
// e.g. team2meta[8] = 3; means that team #8 is on meta team 3
int* initTeamNum2MetaNumLUT()
{
    static int team2meta[30] = {};    // init every element to be 0
    // meta team 1
    team2meta[1]  = 1;
    team2meta[11] = 1;
    team2meta[23] = 1;
    team2meta[28] = 1;

    // meta team 2
    team2meta[2]  = 2;
    team2meta[8]  = 2;
    team2meta[14] = 2;
    team2meta[20] = 2;

    // meta team 3
    team2meta[6]  = 3;
    team2meta[12] = 3;
    team2meta[15] = 3;
    team2meta[26] = 3;

    // meta team 4
    team2meta[5]  = 4;
    team2meta[7]  = 4;
    team2meta[9]  = 4;
    team2meta[24] = 4;

    // meta team 5
    team2meta[4]  = 5;
    team2meta[17] = 5;
    team2meta[18] = 5;
    team2meta[21] = 5;

    // meta team 6
    team2meta[3]  = 6;
    team2meta[10] = 6;
    team2meta[19] = 6;
    team2meta[22] = 6;

    // meta team 7
    team2meta[13] = 7;
    team2meta[16] = 7;
    team2meta[25] = 7;
    team2meta[27] = 7;

    return team2meta;
}

// index of array is the team number, team2bot[idx] = robot number
// e.g. team2bot[8] = 3; means that team #8 is robot number 3 on their respective meta team
int* initTeamNum2BotNumLUT()
{
    static int team2bot[30] = {};    // init every element to be 0
    // meta team 1
    team2bot[1]  = 1;
    team2bot[11] = 2;
    team2bot[23] = 3;
    team2bot[28] = 4;

    // meta team 2
    team2bot[2]  = 1;
    team2bot[8]  = 2;
    team2bot[14] = 3;
    team2bot[20] = 4;

    // meta team 3
    team2bot[6]  = 1;
    team2bot[12] = 2;
    team2bot[15] = 3;
    team2bot[26] = 4;

    // meta team 4
    team2bot[5]  = 1;
    team2bot[7]  = 2;
    team2bot[9]  = 3;
    team2bot[24] = 4;

    // meta team 5
    team2bot[4]  = 1;
    team2bot[17] = 2;
    team2bot[18] = 3;
    team2bot[21] = 4;

    // meta team 6
    team2bot[3]  = 1;
    team2bot[10] = 2;
    team2bot[19] = 3;
    team2bot[22] = 4;

    // meta team 7
    team2bot[13] = 1;
    team2bot[16] = 2;
    team2bot[25] = 3;
    team2bot[27] = 4;

    return team2bot;
}
